import os

import numpy as np
import pandas as pd

from machine_learning.aux.constants import get_processed_data_file_header_segregation
from machine_learning.aux.helpers import read_dataset_csv_file_as_np_arrays
from machine_learning.aux.persist import load_model


def run(model_file: str, in_file: str, out_file: str, stage: int = None):
	"""

	:param model_file:
	:param in_file:
	:param out_file:
	:param stage:
	:return:
	"""

	model_file = os.path.abspath(model_file)
	in_file = os.path.abspath(in_file)
	out_file = os.path.abspath(out_file)

	# load the classifier
	classifier = load_model(model_file)

	# read the dataset
	x_test, z_extra = read_dataset_csv_file_as_np_arrays(in_file, for_training = False)
	# run the classifier on the dataset
	y_pred = classifier.predict(x_test)

	# Predictions.
	# print('Predictions: \n{}'.format(y_pred))
	# The proportion of each cause
	n_pred = y_pred.shape[0]
	print('Causes proportion: {}'.format(np.divide(np.bincount(y_pred.astype(int)), n_pred)))

	# merge arrays to create output array
	# TODO: check
	output_array = np.concatenate((x_test, z_extra), axis = 1)
	output_array = np.concatenate((output_array, np.vstack(y_pred)), axis = 1)

	# create a dataframe
	header = get_processed_data_file_header_segregation(for_training = False)
	header = header[0] + header[1] + ['prediction__label', ]

	# if stage is given add name of labels too
	if stage is not None:
		mapping = None
		if stage == 1:
			from machine_learning.preprocessing.classifier_stage_1.prepare_dataset import get_training_labels
			mapping = get_training_labels()
		if stage == 2:
			from machine_learning.preprocessing.classifier_stage_2.prepare_dataset import get_training_labels
			mapping = get_training_labels()

		if mapping is not None:
			reverse_mapping = dict()
			for key, value in mapping.items():
				reverse_mapping[value] = key

			y_pred_names = list()
			for label in y_pred:
				y_pred_names.append(reverse_mapping[label].name)

			y_pred_names = np.array(y_pred_names)
			# TODO: check
			output_array = np.concatenate((output_array, np.vstack(y_pred_names)), axis = 1)
			header = header + ['prediction__name', ]

	dataframe = pd.DataFrame(data = output_array, columns = header)

	# save dataframe to output
	dataframe.to_csv(out_file, sep = ',', columns = header, header = True, index = False, mode = 'w')


if __name__ == '__main__':
	run(
		'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase__python/machine_learning/saved_models/classifier_stage_2/random_forest.pkl',
		'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase__python/machine_learning/data/test_4_andr_reduced.csv',
		'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase__python/machine_learning/output/test_4_andr.csv',
		stage = 2
		)
