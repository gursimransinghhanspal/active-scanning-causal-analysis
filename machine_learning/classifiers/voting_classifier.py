import itertools
import os

import numpy as np
from sklearn.ensemble import BaggingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier

from machine_learning.aux import directories
from machine_learning.aux.persist import save_model
from machine_learning.metrics import model_stats


def learn_voting_classifier(stratified_data_csv_file, save_filepath):
	# read the stratified dataset
	data = np.genfromtxt(stratified_data_csv_file, delimiter = ',', skip_header = 1)
	X, y = data[:, :-1], data[:, -1]

	# do a 70-30 train-test split.
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30, random_state = 10)

	# classifiers to test
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

	classifier = RandomizedSearchCV(VotingClassifier(estimators = None), params, cv = stratified_k_fold, verbose = 5,
	                                n_jobs = 3)
	classifier.fit(X_train, y_train)
	best_classifier = classifier.best_estimator_
	y_pred = best_classifier.predict(X_test)

	# model statistics
	print('Voting Classifier Statistics')
	print('Best params: {}'.format(classifier.best_params_))
	model_stats.compute_basic_stats(y_test, y_pred)
	model_stats.compute_roc_score(y_test, y_pred)
	model_stats.plot_normalized_confusion_matrix(y_test, y_pred, 'Voting Classifier Normalized Confusion Matrix')

	# fit the classifier on the complete dataset once we get best parameters
	best_classifier = VotingClassifier(**classifier.best_params_)
	best_classifier.fit(X, y)
	# save the model
	save_model(best_classifier, save_filepath)


if __name__ == '__main__':
	# stage 1
	learn_voting_classifier(
		directories.stage_1_stratified_data_csv_file,
		os.path.join(directories.stage_1_saved_models, 'voting_classifier.pkl')
	)
	# stage 2
	learn_voting_classifier(
		directories.stage_2_stratified_data_csv_file,
		os.path.join(directories.stage_2_saved_models, 'voting_classifier.pkl')
	)
