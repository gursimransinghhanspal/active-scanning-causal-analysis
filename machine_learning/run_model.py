import os

import numpy as np

from machine_learning.aux.persist import load_model
from machine_learning.preprocessing.read_dataset import read_labelled_csv_file


def run(model_path, test_data_filepath):
	model_path = os.path.abspath(model_path)
	test_data_filepath = os.path.abspath(test_data_filepath)

	classifier = load_model(model_path)

	# read the dataset.
	X_test = read_labelled_csv_file(test_data_filepath, is_training = False)
	# run the classifier on this dataset.
	y_pred = classifier.predict(X_test)

	# Predictions.
	# print('Predictions: \n{}'.format(y_pred))
	# The proportion of each cause
	n_pred = y_pred.shape[0]
	print('Causes proportion: {}'.format(np.divide(np.bincount(y_pred.astype(int)), n_pred)))


if __name__ == '__main__':
	run('/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase/machine_learning/saved_models/stage_1/random_forest.pkl',
		'/Users/gursimran/Workspace/active-scanning-cause-analysis/codebase/machine_learning/data/stage_1/unlabeled_data.csv')
