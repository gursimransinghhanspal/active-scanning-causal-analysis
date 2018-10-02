import itertools
import os

import numpy as np
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, f1_score, make_scorer, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

from machine_learning.aux.persist import save_model
from machine_learning.metrics import model_stats


def learn(training_data_infile, trained_model_outfile = None, display_metrics: bool = False, gs_verbose: int = 0,
          n_jobs = 1):
	"""
	Trains a voting classifier

	:param training_data_infile: Csv file containing training data (labeled)
								 • The last column should be training labels
								 • Csv file can contain header (line 1 is skipped)
								 • Use: machine_learning.aux.data_processing.create_training_dataset

	:param trained_model_outfile: where to save the model
	:param display_metrics: whether to print model metrics or not
	:param gs_verbose: verbosity of GridSearch
	:param n_jobs: GridSearch parallel jobs
	:return:
	"""

	training_data_infile = os.path.abspath(training_data_infile)

	# start
	print('-' * 25)
	print('Starting learning for `Voting Classifier`')
	print('training_infile: {:s}'.format(str(os.path.relpath(training_data_infile))))
	print('trained_outfile: {:s}'.format(
		str(os.path.relpath(trained_model_outfile)) if trained_model_outfile is not None else 'None'
	))
	print('display_metric: {:s}, gs_verbose: {:d}, n_jobs: {:d}'.format(str(display_metrics), gs_verbose, n_jobs))
	print()

	# read the stratified dataset
	data = np.genfromtxt(training_data_infile, delimiter = ',', skip_header = 1)
	features_x, target_y = data[:, :-1], data[:, -1]

	# do a 70-30 train-test split.
	x_train, x_test, y_train, y_test = train_test_split(features_x, target_y, test_size = 0.30)

	scaler = StandardScaler()
	features_x = scaler.fit_transform(features_x)
	x_train = scaler.fit_transform(x_train)
	x_test = scaler.fit_transform(x_test)

	# classifier to test
	classifiers = [
		# ('dt', DecisionTreeClassifier(max_depth = None, min_samples_split = 2)),
		('knn', KNeighborsClassifier(n_neighbors = 5)),
		# ('lin_svm', SVC(C = 100.0, kernel = 'linear')),
		# ('logreg', LogisticRegression(C = '100.0', max_iter = '200', penalty = 'l1')),
		('nb', GaussianNB()),
		# ('rbf_svm', SVC(C = 100.0, gamma = 0.1, kernel = 'rbf')),
		('rf', RandomForestClassifier(max_depth = 20, min_samples_split = 5, n_estimators = 30)),
		('sgd', SGDClassifier(alpha = 0.0001, loss = 'log', max_iter = 200, penalty = 'l2')),
		('bagging', BaggingClassifier(
			base_estimator = None, max_features = 0.75, max_samples = 0.5, n_estimators = 30
		)),
		# ('boosting', GradientBoostingClassifier(
		# 	learning_rate = 0.1, max_depth = 5, min_samples_split = 5, n_estimators = 300
		# ))
	]

	# create all possible combinations
	combinations_ = list()
	for i in range(len(classifiers)):
		combinations_.extend(list(itertools.combinations(classifiers, i + 1)))

	# testing parameters
	params = {
		'estimators': combinations_,
		'voting': ['soft', 'hard', ],
	}
	stratified_k_fold = StratifiedKFold(n_splits = 10)
	classifier = RandomizedSearchCV(
		VotingClassifier(estimators = None),
		params,
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

	classifier.fit(x_train, y_train)
	best_classifier = classifier.best_estimator_
	y_pred = best_classifier.predict(x_test)

	print('Voting Classifier Statistics')
	print('Best params: {}'.format(classifier.best_params_))
	model_stats.compute_basic_stats(y_test, y_pred)
	model_stats.compute_roc_score(y_test, y_pred)
	model_stats.plot_normalized_confusion_matrix(
		y_test, y_pred, 'Voting Classifier Normalized Confusion Matrix'
	)

	# fit the classifier on the complete dataset once we get best parameters
	complete_classifier = VotingClassifier(**classifier.best_params_)
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


if __name__ == '__main__':
	pass
