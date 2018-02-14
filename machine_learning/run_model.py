import sys

import numpy as np

from machine_learning.aux.persist import load_classifier
from machine_learning.preprocessing.read_dataset import read_labelled_csv_file


def run():
	# Name of the model we want to load. This is the first command line argument.
	model_name = sys.argv[1]

	# Name of the csv file containing the test data. This is the second command line argument.
	test_data_file = sys.argv[2]

	"""
	For example: $ python3 test_module.py random_forest data.csv
	"""

	clf = load_classifier('models/' + model_name + '.pkl')

	# Read the dataset.
	X_test = read_labelled_csv_file(test_data_file)
	# print(X_test[0])
	# Run the classifier on this dataset.
	y_pred = clf.predict(X_test)

	# Predictions.
	# print('Predictions: \n{}'.format(y_pred))
	# The proportion of each cause
	n_pred = y_pred.shape[0]
	print('Causes proportion: {}'.format(np.divide(np.bincount(y_pred.astype(int)), n_pred)))


if __name__ == '__main__':
	run()
