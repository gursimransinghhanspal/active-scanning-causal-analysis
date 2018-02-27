import os

import numpy as np
import pandas as pd

from machine_learning.aux import constants, directories, helpers
from machine_learning.aux.constants import get_processed_data_file_header_segregation, get_training_label_header
from machine_learning.aux.helpers import read_dataset_csv_file_as_np_arrays


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


def get_processed_csv_file_names(directory_path):
	"""
	Read all the file names present in the given directory
	"""
	__supported_extensions = ['.csv', ]

	processed_csv_file_names = list()

	listdir = os.listdir(directory_path)
	for file in listdir:
		if os.path.splitext(file)[1] in __supported_extensions:
			processed_csv_file_names.append(file)

	# sort so that we always read in a predefined order
	# key: smallest file first
	processed_csv_file_names.sort(key = lambda f: os.path.getsize(os.path.join(directory_path, f)))
	return processed_csv_file_names


def get_training_label_proportions():
	"""
	Mapping from as-causes to training label proportions for stage 1 classifier
	"""

	mapping = dict()
	mapping[2] = 600
	mapping[1] = 0
	mapping[0] = 0
	return mapping


def merge_and_label_processed_csv_files(outfile, training_labels, for_training: bool = True):
	"""
	Merges all the csv files in `processed_files` directory in a single csv file.
		- If `for_training` == True, then the training sub-directory is used and the data is also labeled
		  according to the folder the files are in.
		- Else, the testing subdirectory is used.
	"""

	def label_and_append_processed_csv_file(_filename, _write_filepath, required_columns,
	                                        _cause = None):
		_dataframe = helpers.read_csv_file(_filename)
		_dataframe = _dataframe[required_columns]

		if not os.path.exists(_write_filepath):
			_should_add_header = True
		else:
			_should_add_header = False

		header = list(required_columns)
		if _cause is not None:
			head_training = get_training_label_header()
			_dataframe[head_training] = training_labels[_cause]
			header.append(head_training)

		_dataframe.to_csv(_write_filepath, mode = 'a', columns = header, header = _should_add_header,
		                  index = False)
		return _dataframe.shape[0]

	# required columns
	# used to choose only the required columns from the input processed episode csv
	head_features, head_properties = get_processed_data_file_header_segregation(for_training = False)
	req_columns = head_features + head_properties

	# count of number of instances
	instance_count = 0

	if for_training:
		# delete dataset files if they exist
		directories.delete_file(outfile)

		# get label info
		training_data_directories = constants.get_training_data_directories()

		# assign labels and merge
		for cause, directory in training_data_directories.items():
			if cause not in training_labels.keys():
				continue

			csv_filenames = get_processed_csv_file_names(directory)
			for filename in csv_filenames:
				csv_filename = os.path.abspath(os.path.join(directory, filename))
				instance_count += label_and_append_processed_csv_file(csv_filename, outfile,
				                                                      required_columns = req_columns, _cause = cause)

			print('• Total instance count for cause "{:s}":'.format(cause.name), instance_count)
			instance_count = 0
	else:
		# delete dataset files if they exist
		directories.delete_file(outfile)

		# get label info
		testing_data_directory = directories.processed_files_testing

		# merge
		csv_filenames = get_processed_csv_file_names(testing_data_directory)
		for filename in csv_filenames:
			csv_filename = os.path.abspath(os.path.join(testing_data_directory, filename))
			instance_count += label_and_append_processed_csv_file(csv_filename, outfile, required_columns = req_columns,
			                                                      _cause = None)

		print('• Total instance count:', instance_count)


def create_training_dataset(infile, outfile, proportions = None):
	"""
	Creates training dataset using the complete merged dataset file.
	"""

	X, y, _ = read_dataset_csv_file_as_np_arrays(infile, for_training = True)
	print(np.bincount(y.astype(int)))

	# concatenate features and target
	X_temp = np.concatenate((X, np.vstack(y)), axis = 1)

	X_final = None

	# stratify if proportions are given
	if proportions is not None:
		for label, sample_size in proportions.items():
			X_label = X_temp[np.where(y == label)]
			X_label = X_label[np.random.choice(X_label.shape[0], sample_size, replace = False)]

			if X_final is None:
				X_final = np.array(X_label)
			else:
				X_final = np.append(X_final, X_label, axis = 0)
	else:
		X_final = X_temp

	if X_final is not None:
		# required columns (header)
		head_features, head_training, head_properties = get_processed_data_file_header_segregation(for_training = True)
		header = head_features + head_properties + head_training

		# save array to outfile
		dataframe = pd.DataFrame(data = X_final, columns = header)
		dataframe.to_csv(outfile, sep = ',', columns = header, header = True, index = False, mode = 'w')


if __name__ == '__main__':
	pass
