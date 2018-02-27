import os

import numpy as np

from machine_learning.aux import constants, helpers
from machine_learning.aux.constants import get_processed_data_file_header_segregation
from machine_learning.aux.helpers import read_dataset_csv_file_as_np_arrays
from machine_learning.aux.persist import load_model
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


def identify_pscans_using_stage_1_classifier(infile, outfile, classifier_filepath, for_training):
	"""
	Removes periodic scan instances from the training dataset using stage 1 classifier
	"""

	def remove_unassociated_pscans(_dataframe, pred):
		# stage 1 training labels
		stage_1_training_labels = get_stage_1_training_labels()

		indexes_to_drop = list()
		for idx, label in enumerate(pred):
			if label == stage_1_training_labels[constants.ASCause.pscan_unassoc]:
				indexes_to_drop.append(idx)

		indexes_to_keep = set(range(_dataframe.shape[0])) - set(indexes_to_drop)
		return _dataframe.take(list(indexes_to_keep))

	def remove_associated_pscans(_dataframe, pred):
		# stage 1 training labels
		stage_1_training_labels = get_stage_1_training_labels()

		indexes_to_drop = list()
		for idx, label in enumerate(pred):
			if label == stage_1_training_labels[constants.ASCause.pscan_assoc]:
				indexes_to_drop.append(idx)

		indexes_to_keep = set(range(_dataframe.shape[0])) - set(indexes_to_drop)
		return _dataframe.take(list(indexes_to_keep))

	infile = os.path.abspath(infile)
	outfile = os.path.abspath(outfile)
	classifier_filepath = os.path.abspath(classifier_filepath)
	classifier = load_model(classifier_filepath)

	# read the data to predict labels for
	features_x, _ = read_dataset_csv_file_as_np_arrays(filepath = infile, for_training = False)
	y_pred = classifier.predict(features_x)

	# some insight
	n_pred = y_pred.shape[0]
	print('• Periodic Scans prediction count: {}'.format(np.bincount(y_pred.astype(int))))
	print('• Periodic Scans prediction proportion: {}'.format(np.divide(np.bincount(y_pred.astype(int)), n_pred)))

	# read in the datafile
	dataframe = helpers.read_csv_file(infile)
	print('• Dataframe shape before dropping identified pscans:', dataframe.shape)
	# remove unassociated per_scans
	dataframe = remove_unassociated_pscans(dataframe, y_pred)
	print('• Dataframe shape after dropping identified unassociated pscans:', dataframe.shape)
	# remove associated per_scans
	dataframe = remove_associated_pscans(dataframe, y_pred)
	print('• Dataframe shape after dropping identified associated pscans:', dataframe.shape)

	# write the file back
	if for_training:
		head_features, head_training, head_properties = get_processed_data_file_header_segregation(for_training = True)
		header = head_features + head_properties + head_training
	else:
		head_features, head_properties = get_processed_data_file_header_segregation(for_training = False)
		header = head_features + head_properties
	dataframe.to_csv(outfile, columns = header, header = True, index = False, mode = 'w')


if __name__ == '__main__':
	pass
