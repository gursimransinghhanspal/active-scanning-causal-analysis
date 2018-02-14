import os

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler

from machine_learning.aux import directories
from machine_learning.aux.persist import save_model
from machine_learning.metrics import model_stats


def learn_logreg(stratified_data_csv_file, save_filepath):
	# read the stratified dataset
	data = np.genfromtxt(stratified_data_csv_file, delimiter = ',')
	X, y = data[:, :-1], data[:, -1]

	# do a 70-30 train-test split.
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30, random_state = 10)

	# standardize train and test data (scale X_train to [0, 1] range)
	scaler = StandardScaler().fit(X_train)
	X_train = scaler.fit_transform(X_train)
	X_test = scaler.fit_transform(X_test)

	# testing parameters
	params = {
		'penalty': ['l1', 'l2'],
		'C': np.logspace(-2, 2, 5),
		'max_iter': [200]
	}
	stratified_k_fold = StratifiedKFold(n_splits = 10)

	classifier = GridSearchCV(LogisticRegression(), params, cv = stratified_k_fold, verbose = 5)
	classifier.fit(X_train, y_train)
	best_classifier = classifier.best_estimator_
	y_pred = best_classifier.predict(X_test)

	# model statistics
	print('Logistic Regression Model Statistics')
	print('Best params: {0}'.format(classifier.best_params_))
	model_stats.compute_basic_stats(y_test, y_pred)
	model_stats.compute_roc_score(y_test, y_pred)
	model_stats.plot_normalized_confusion_matrix(
		y_test, y_pred, 'Logistic Regression Classifier Normalized Confusion Matrix'
	)

	# fit the classifier on the complete dataset once we get best parameters
	best_classifier = LogisticRegression(**classifier.best_params_)
	best_classifier.fit(X, y)
	# save the model
	save_model(best_classifier, save_filepath)


if __name__ == '__main__':
	# stage 1
	learn_logreg(
		directories.stage_1_stratified_data_csv_file,
		os.path.join(directories.stage_1_saved_models, 'logistic_regression.pkl')
	)
	# stage 2
	learn_logreg(
		directories.stage_2_stratified_data_csv_file,
		os.path.join(directories.stage_2_saved_models, 'logistic_regression.pkl')
	)
