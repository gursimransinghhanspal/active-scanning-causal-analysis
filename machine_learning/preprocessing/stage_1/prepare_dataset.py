import os

import numpy as np

from machine_learning.aux import constants, directories, helpers
from machine_learning.preprocessing.read_dataset import read_labelled_csv_file


def get_training_labels():
	"""
	Mapping from as-causes to training labels for stage 1 classifier
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

	Labels ->   0, if periodic scan unassociated
				1, if periodic scan associated
				2, if any other cause
	"""

	if training:
		training_labels = get_training_labels()
		training_data_directories = constants.get_training_data_directories()

		for cause, directory in training_data_directories.items():
			csv_filenames = get_processed_csv_file_names(directory)

			for filename in csv_filenames:
				csv_file = os.path.join(directory, filename)
				dataframe = helpers.read_processed_csv_file(csv_file)

				if cause in training_labels.keys():
					dataframe['label'] = training_labels[cause]

				# TODO: remove 'cause' from processed csv
				# drop frames where 'cause' is not available
				dataframe['cause'].replace('', np.nan, inplace = True)
				dataframe.dropna(subset = ['cause'], inplace = True)
				dataframe.fillna(0)

				if not os.path.exists(directories.stage_1_labeled_data_csv_file):
					should_add_header = False
				else:
					should_add_header = False

				dataframe.to_csv(directories.stage_1_labeled_data_csv_file, mode = 'a',
				                 header = should_add_header, index = False)
	else:
		testing_data_directory = directories.processed_files_testing
		csv_filenames = get_processed_csv_file_names(testing_data_directory)

		for filename in csv_filenames:
			csv_file = os.path.join(testing_data_directory, filename)
			dataframe = helpers.read_processed_csv_file(csv_file)

			# TODO: remove 'cause' from processed csv
			# drop frames where 'cause' is not available
			dataframe['cause'].replace('', np.nan, inplace = True)
			dataframe.dropna(subset = ['cause'], inplace = True)
			dataframe.fillna(0)

			if not os.path.exists(directories.stage_1_unlabeled_data_csv_file):
				should_add_header = False
			else:
				should_add_header = False

			dataframe.to_csv(directories.stage_1_unlabeled_data_csv_file, mode = 'a',
			                 header = should_add_header, index = False)


# Read specific number of examples for each label.
def stratify_labeled_dataset():
	X, y = read_labelled_csv_file(directories.stage_1_labeled_data_csv_file)

	print(np.bincount(y.astype(int)))

	X_temp = np.concatenate((X, np.vstack(y)), axis = 1)
	X_final = []
	for label in range(3):
		# Number of examples to read for the current label.
		X_label = X_temp[np.where(y == label)]

		if label == 0:
			X_final = np.array(X_label)
		else:
			X_final = np.append(X_final, X_label, axis = 0)
	np.savetxt(
		directories.stage_1_stratified_data_csv_file, X_final, delimiter = ",",
		# fmt = '%d,%d,%d,%d,%d,%d,%.18e,%.18e,%d,%.18e,%.18e,%d,%d'
	)


merge_processed_csv_files(True)
stratify_labeled_dataset()
