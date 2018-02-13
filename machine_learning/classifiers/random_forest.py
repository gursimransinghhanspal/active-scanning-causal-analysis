import os

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split

from machine_learning.aux import directories
from machine_learning.aux.persist import save_classifier
from machine_learning.metrics.model_stats import compute_basic_stats, compute_roc_score, \
	plot_normalized_confusion_matrix


def rf_classifier():
	# Read the dataset.
	data = np.genfromtxt(directories.stage_1_stratified_data_csv_file, delimiter = ',')
	X, y = data[:, :-1], data[:, -1]
	# Do a 70-30 train-test split.
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30, random_state = 10)

	params = {'n_estimators': [5, 10, 20, 30], 'max_depth': [None, 5, 10, 20, 30], 'min_samples_split': [2, 5, 10]}
	stratified_k_fold = StratifiedKFold(n_splits = 10)
	clf = GridSearchCV(RandomForestClassifier(), params, cv = stratified_k_fold, verbose = 5)
	clf.fit(X_train, y_train)

	best_clf = clf.best_estimator_
	y_pred = best_clf.predict(X_test)

	print('Best params: {}'.format(clf.best_params_))
	print('Random Forest Model Statistics')
	compute_basic_stats(y_test, y_pred)
	compute_roc_score(y_test, y_pred)
	plot_normalized_confusion_matrix(y_test, y_pred, 'Random Forest Classifier Normalized Confusion Matrix')

	# Fit the classifier on the complete dataset once we get best parameters
	best_clf = RandomForestClassifier(**clf.best_params_)
	best_clf.fit(X, y)

	# Save the model
	save_classifier(best_clf, os.path.join(directories.stage_1_saved_models, 'random_forest'))


if __name__ == '__main__':
	rf_classifier()
