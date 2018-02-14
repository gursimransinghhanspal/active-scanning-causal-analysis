import os

import numpy as np

from machine_learning.aux import constants, directories, helpers
from machine_learning.preprocessing.read_dataset import label_column_name, read_labelled_csv_file, required_features


def get_training_labels():
	"""
	Mapping from as-causes to training labels for stage 1 classifier

	Labels ->   0, if periodic scan unassociated
				1, if periodic scan associated
				2, if any other cause
	"""

	mapping = dict()
	mapping[constants.ASCause.apsp] = 2
	mapping[constants.ASCause.bl] = 2
	mapping[constants.ASCause.ce] = 2
	mapping[constants.ASCause.dfl] = 2
	mapping[constants.ASCause.lrssi] = 2
	mapping[constants.ASCause.pscan_assoc] = 1
	mapping[constants.ASCause.pscan_unassoc] = 0
	mapping[constants.ASCause.pwr_state] = 2
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


def merge_processed_csv_files(training: bool = True):
	"""
	Merges all the csv files in `processed_files` directory in a single csv file.
	If `training` == True, then the training sub-directory is used and the data is also labeled
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

	if training:
		# delete data files if exist
		directories.delete_file(directories.stage_1_labeled_data_csv_file)
		directories.delete_file(directories.stage_1_stratified_data_csv_file)

		training_labels = get_training_labels()
		training_data_directories = constants.get_training_data_directories()

		for cause, directory in training_data_directories.items():
			csv_filenames = get_processed_csv_file_names(directory)

			for filename in csv_filenames:
				merge(directory, filename, directories.stage_1_labeled_data_csv_file, cause)

		stratify_labeled_dataset()

	else:
		# delete data files if exist
		directories.delete_file(directories.stage_1_unlabeled_data_csv_file)

		testing_data_directory = directories.processed_files_testing
		csv_filenames = get_processed_csv_file_names(testing_data_directory)

		for filename in csv_filenames:
			merge(testing_data_directory, filename, directories.stage_1_unlabeled_data_csv_file)


def stratify_labeled_dataset():
	X, y = read_labelled_csv_file(directories.stage_1_labeled_data_csv_file)
	print('Complete data bincount:', np.bincount(y.astype(int)))

	X_temp = np.concatenate((X, np.vstack(y)), axis = 1)

	X_final = None
	for label in range(3):
		X_label = X_temp[np.where(y == label)]

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
			directories.stage_1_stratified_data_csv_file, X_final, delimiter = ',',
			header = header_string, comments = '',
			fmt = '%d,%d,%d,%d,%d,%d,%.18e,%.18e,%d,%.18e,%.18e,%d,%d'
		)


if __name__ == '__main__':
	merge_processed_csv_files(training = True)
