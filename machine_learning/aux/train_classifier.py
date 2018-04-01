import os

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, make_scorer, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler

from machine_learning.aux.persist import save_model
from machine_learning.metrics import model_stats


def train_classifier_using_grid_search(classifier_name: str, classifier_object, gs_params: dict, training_data_infile,
                                       trained_model_outfile = None, display_metrics: bool = False, gs_verbose: int = 0,
                                       n_jobs = 1, normalize: bool = False):
	"""
	Trains a given classifier model

	:param classifier_name:
	:param classifier_object:
	:param gs_params: Parameters for GridSearchCV
	:param training_data_infile: Csv file containing training data (labeled)
								 • The last column should be training labels
								 • Csv file can contain header (line 1 is skipped)
								 • Use: machine_learning.aux.preprocessor.create_training_dataset

	:param trained_model_outfile: where to save the model
	:param display_metrics: whether to print model metrics or not
	:param gs_verbose: verbosity of GridSearch
	:param n_jobs: GridSearch parallel jobs
	:param normalize:
	:return: trained model
	"""

	training_data_infile = os.path.abspath(training_data_infile)

	# start
	print('-' * 25)
	print('Starting learning for `{:s}`'.format(classifier_name))
	print('training_infile: {:s}'.format(str(os.path.relpath(training_data_infile))))
	print('trained_outfile: {:s}'.format(
		str(os.path.relpath(trained_model_outfile)) if trained_model_outfile is not None else 'None'
	))
	print('display_metric: {:s}, gs_verbose: {:d}, n_jobs: {:d}'.format(str(display_metrics), gs_verbose, n_jobs))
	print()

	# read the stratified dataset
	data = np.genfromtxt(training_data_infile, delimiter = ',', skip_header = 1)
	features_x, target_y = data[:, :-1], data[:, -1]

	# print(features_x.shape)
	# print(target_y.shape)

	# do a 70-30 train-test split.
	x_train, x_test, y_train, y_test = train_test_split(features_x, target_y, test_size = 0.30)

	# print(x_train.shape)
	# print(x_test.shape)
	# print(y_train.shape)
	# print(y_test.shape)

	if normalize:
		scaler = StandardScaler()
		features_x = scaler.fit_transform(features_x)
		x_train = scaler.fit_transform(x_train)
		x_test = scaler.fit_transform(x_test)

	stratified_k_fold = StratifiedKFold(n_splits = 10)
	classifier = GridSearchCV(
		classifier_object(),
		gs_params,
		cv = stratified_k_fold,
		scoring = {
			'accuracy': make_scorer(accuracy_score),
			'precision': make_scorer(precision_score),
			'recall': make_scorer(recall_score),
			'roc_auc': make_scorer(roc_auc_score),
			'f1': make_scorer(f1_score),
		},
		refit = 'f1',
		verbose = gs_verbose,
		n_jobs = n_jobs
	)

	# print best model metrics
	if display_metrics:
		classifier.fit(x_train, y_train)
		best_classifier = classifier.best_estimator_
		y_pred = best_classifier.predict(x_test)

		print('{:s} Classifier Statistics'.format(classifier_name))
		print('Best params: {}'.format(classifier.best_params_))
		model_stats.compute_basic_stats(y_test, y_pred)
		model_stats.compute_roc_score(y_test, y_pred)
		model_stats.plot_normalized_confusion_matrix(
			y_test, y_pred, '{:s} Classifier Normalized Confusion Matrix'.format(classifier_name)
		)

	# fit the classifier on the complete dataset once we get best parameters
	complete_classifier = classifier_object(**classifier.best_params_)
	complete_classifier.fit(features_x, target_y)

	# save the model
	if trained_model_outfile:
		try:
			trained_model_outfile = os.path.abspath(trained_model_outfile)
			save_model(complete_classifier, trained_model_outfile)
			print('Classifier successfully saved at: {:s}'.format(str(os.path.relpath(trained_model_outfile))))
		except Exception as exc:
			print('Error while saving model! Could not save at: '
			      '{:s}'.format(str(os.path.relpath(trained_model_outfile))))
			print(exc)

	print('-' * 25)
	return complete_classifier
