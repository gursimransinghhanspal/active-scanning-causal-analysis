import os

import numpy as np
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.naive_bayes import GaussianNB

from machine_learning.aux import directories
from machine_learning.aux.persist import save_model
from machine_learning.metrics import model_stats


def learn_naive_bayes(stratified_data_csv_file, save_filepath):
	# read the stratified dataset
	data = np.genfromtxt(stratified_data_csv_file, delimiter = ',', skip_header = 1)
	X, y = data[:, :-1], data[:, -1]

	# do a 70-30 train-test split.
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30, random_state = 10)

	# testing parameters
	params = {}
	stratified_k_fold = StratifiedKFold(n_splits = 10)

	classifier = GridSearchCV(GaussianNB(), params, cv = stratified_k_fold, verbose = 5)
	classifier.fit(X_train, y_train)
	best_classifier = classifier.best_estimator_
	y_pred = best_classifier.predict(X_test)

	# model statistics
	print('Naive Bayes Model Statistics')
	print('Best params: {0}'.format(classifier.best_params_))
	model_stats.compute_basic_stats(y_test, y_pred)
	model_stats.compute_roc_score(y_test, y_pred)
	model_stats.plot_normalized_confusion_matrix(y_test, y_pred, 'Naive Bayes Classifier Normalized Confusion Matrix')

	# fit the classifier on the complete dataset once we get best parameters
	best_classifier = GaussianNB(**classifier.best_params_)
	best_classifier.fit(X, y)
	# save the model
	save_model(best_classifier, save_filepath)


if __name__ == '__main__':
	# stage 1
	learn_naive_bayes(
		directories.stage_1_stratified_data_csv_file,
		os.path.join(directories.stage_1_saved_models, 'naive_bayes.pkl')
	)
	# stage 2
	# learn_naive_bayes(
	# 	directories.stage_2_stratified_data_csv_file,
	# 	os.path.join(directories.stage_2_saved_models, 'naive_bayes.pkl')
	# )
