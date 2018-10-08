import os

import numpy as np

from machine_learning.aux import constants, helpers
from machine_learning.aux.constants import get_processed_data_file_header_segregation
from machine_learning.aux.helpers import read_dataset_csv_file_as_np_arrays
from machine_learning.aux.persist import load_model
from machine_learning.preprocessing.classifier_stage_1.prepare_dataset import get_training_labels as get_stage_1_training_labels, \
	merge_and_label_processed_csv_files


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





if __name__ == '__main__':
	merge_and_label_processed_csv_files(
		'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase__python/machine_learning/data/test_4_andr.csv',
		get_training_labels(),
		for_training = False
	)

	identify_pscans_using_stage_1_classifier(
		'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase__python/machine_learning/data/test_4_andr.csv',
		'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase__python/machine_learning/data/test_4_andr_reduced.csv',
		'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase__python/machine_learning/saved_models/classifier_stage_1/random_forest.pkl',
		for_training = False
	)

	# create_training_dataset(
	# 	'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase/machine_learning/data/classifier_stage_2/reduced_dataset.csv',
	# 	'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase/machine_learning/data/classifier_stage_2/training_dataset.csv',
	# 	get_training_label_proportions()
	# )
	pass
