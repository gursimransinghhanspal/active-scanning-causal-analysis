import os

import numpy as np
import pandas as pd

from machine_learning.aux import constants, directories, helpers
from machine_learning.aux.persist import load_model
from machine_learning.preprocessing.read_dataset import label_column_name, read_labelled_csv_file, required_features
from machine_learning.preprocessing.stage_1.prepare_dataset import get_training_labels as get_stage_1_training_labels


def get_training_labels():
	"""
	Mapping from as-causes to training labels for stage 2 classifier

	Labels ->   0, APSP
				1, BL
				2, CE
				3, DFL
				4, LRSSI
				5, PWR_STATE
	"""

	mapping = dict()
	mapping[constants.ASCause.apsp] = 0
	mapping[constants.ASCause.bl] = 1
	mapping[constants.ASCause.ce] = 2
	mapping[constants.ASCause.dfl] = 3
	mapping[constants.ASCause.lrssi] = 4
	mapping[constants.ASCause.pwr_state] = 5
	return mapping


def get_training_label_proportions():
	"""
	Mapping from as-causes to training label proportions for stage 2 classifier
	"""

	label_mapping = get_training_labels()

	mapping = dict()
	mapping[label_mapping[constants.ASCause.apsp]] = 575
	mapping[label_mapping[constants.ASCause.bl]] = 500
	mapping[label_mapping[constants.ASCause.ce]] = 449
	mapping[label_mapping[constants.ASCause.dfl]] = 114
	mapping[label_mapping[constants.ASCause.lrssi]] = 600
	mapping[label_mapping[constants.ASCause.pwr_state]] = 449
	return mapping


SUPPORTED_EXTS = ['.csv', ]


def get_processed_csv_file_names(directory_path):
	"""
	Read all the file names present in the given directory
	"""

	processed_csv_file_names = list()

	listdir = os.listdir(directory_path)
	for file in listdir:
		if os.path.splitext(file)[1] in SUPPORTED_EXTS:
			processed_csv_file_names.append(file)

	# sort so that we always read in a predefined order
	# key: smallest file first
	processed_csv_file_names.sort(key = lambda f: os.path.getsize(os.path.join(directory_path, f)))
	return processed_csv_file_names


def merge_processed_csv_files(is_training: bool = True, stage_1_model_path = None):
	"""
	Merges all the csv files in `processed_files` directory in a single csv file.
	If `is_training` == True, then the is_training sub-directory is used and the data is also labeled
	according to the folder the files are in.
	"""

	def merge(_read_directory, _read_filename, _write_filepath, _cause = None):
		_csv_file = os.path.join(_read_directory, _read_filename)
		_dataframe = helpers.read_processed_csv_file(_csv_file)

		_dataframe = _dataframe[required_features]
		_dataframe.fillna(0)

		if not os.path.exists(_write_filepath):
			_should_add_header = True
		else:
			_should_add_header = False

		output_columns = list(required_features)
		if _cause is not None:
			_dataframe[label_column_name] = training_labels[_cause]
			output_columns.append(label_column_name)

		_dataframe.to_csv(_write_filepath, mode = 'a', columns = output_columns, header = _should_add_header, index = False)

	if is_training:
		_write_file = directories.stage_2_stratified_data_csv_file

		# delete data files if exist
		directories.delete_file(directories.stage_2_labeled_data_csv_file)
		directories.delete_file(_write_file)

		training_labels = get_training_labels()
		training_data_directories = constants.get_training_data_directories()

		for cause, directory in training_data_directories.items():
			if cause not in training_labels.keys():
				continue

			csv_filenames = get_processed_csv_file_names(directory)
			for filename in csv_filenames:
				merge(directory, filename, directories.stage_2_labeled_data_csv_file, cause)

		stratify_labeled_dataset(directories.stage_2_labeled_data_csv_file)
		data_file = _write_file

	else:
		_write_file = directories.stage_2_unlabeled_data_csv_file

		# delete data files if exist
		directories.delete_file(_write_file)

		testing_data_directory = directories.processed_files_testing
		csv_filenames = get_processed_csv_file_names(testing_data_directory)

		for filename in csv_filenames:
			merge(testing_data_directory, filename, _write_file)

		data_file = _write_file

	if data_file is not None and stage_1_model_path is not None:
		stage_1_model_path = os.path.abspath(stage_1_model_path)
		process_stage_2_learning_data(data_file, stage_1_model_path, is_training)


def stratify_labeled_dataset(_write_file):
	X, y = read_labelled_csv_file(_write_file)
	print(np.bincount(y.astype(int)))

	X_temp = np.concatenate((X, np.vstack(y)), axis = 1)

	X_final = None
	proportions = get_training_label_proportions()
	for label, sample_size in proportions.items():
		X_label = X_temp[np.where(y == label)]
		X_label = X_label[np.random.choice(X_label.shape[0], sample_size, replace = False)]

		if X_final is None:
			X_final = np.array(X_label)
		else:
			X_final = np.append(X_final, X_label, axis = 0)

	if X_final is not None:
		# stratify_labeled_dataset() only runs for training, so append `label` to header
		output_columns = list(required_features)
		output_columns.append(label_column_name)
		header_string = ','.join(output_columns)

		np.savetxt(
			directories.stage_2_stratified_data_csv_file, X_final, delimiter = ',',
			header = header_string, comments = '',
			fmt = '%d,%d,%d,%d,%d,%d,%.18e,%.18e,%d,%.18e,%.18e,%d,%d'
		)


def process_stage_2_learning_data(data_filepath, model_path, is_training: bool):
	"""
	Removes periodic scan instances from the training dataset using stage 1 classifier
	"""

	def remove_unassociated_pscans(_dataframe, pred):
		indexes_to_drop = list()
		for idx, label in enumerate(pred):
			if label == stage_1_training_labels[constants.ASCause.pscan_unassoc]:
				indexes_to_drop.append(idx)

		indexes_to_keep = set(range(_dataframe.shape[0])) - set(indexes_to_drop)
		return _dataframe.take(list(indexes_to_keep))

	def remove_associated_pscans(_dataframe, pred):
		indexes_to_drop = list()
		for idx, label in enumerate(pred):
			if label == stage_1_training_labels[constants.ASCause.pscan_assoc]:
				indexes_to_drop.append(idx)

		indexes_to_keep = set(range(_dataframe.shape[0])) - set(indexes_to_drop)
		return _dataframe.take(list(indexes_to_keep))

	classifier = load_model(model_path)

	# read the data to predict labels for
	X_test = read_labelled_csv_file(filepath = data_filepath, is_training = False)
	y_pred = classifier.predict(X_test)
	n_pred = y_pred.shape[0]
	print('Stage 1 prediction proportion: {}'.format(np.divide(np.bincount(y_pred.astype(int)), n_pred)))

	# stage 1 training labels
	stage_1_training_labels = get_stage_1_training_labels()

	input_columns = list(required_features)
	if is_training:
		input_columns.append(label_column_name)

	# read in the datafile
	dataframe = pd.read_csv(
		filepath_or_buffer = data_filepath,
		sep = ',',  # comma separated values (default)
		header = None,
		names = input_columns,
		index_col = None,  # do not use any column to index
		skipinitialspace = True,  # skip any space after delimiter
		na_values = ['', ],  # values to consider as `not available`
		na_filter = True,  # detect `not available` values
		skip_blank_lines = True,  # skip any blank lines in the file
		float_precision = 'high'
	)
	print('Stage 2 instances before dropping: {:d}'.format(len(dataframe)))

	# remove unassociated per_scans
	dataframe = remove_unassociated_pscans(dataframe, y_pred)
	print('Stage 2 instances after dropping unassociated per scans: {:d}'.format(len(dataframe)))

	# remove associated per_scans
	dataframe = remove_associated_pscans(dataframe, y_pred)
	print('Stage 2 instances after dropping associated per scans: {:d}'.format(len(dataframe)))

	# write the file back
	dataframe.to_csv(data_filepath, mode = 'w', columns = required_features, header = False, index = False)


if __name__ == '__main__':
	merge_processed_csv_files(is_training = True,
	                          stage_1_model_path = '/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase/machine_learning/saved_models/stage_1/random_forest.pkl')
