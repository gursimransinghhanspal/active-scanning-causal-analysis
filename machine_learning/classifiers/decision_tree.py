import os

import numpy as np
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.tree import DecisionTreeClassifier

from machine_learning.aux import directories
from machine_learning.aux.persist import save_model
from machine_learning.metrics import model_stats


def learn_decision_tree(stratified_data_csv_file, save_filepath):
	# read the stratified dataset
	data = np.genfromtxt(stratified_data_csv_file, delimiter = ',', skip_header = 1)
	X, y = data[:, :-1], data[:, -1]

	# do a 70-30 train-test split.
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30, random_state = 10)

	# testing parameters
	params = {
		'max_depth': [None, 5, 10, 20, 30],
		'min_samples_split': [2, 5, 10]
	}
	stratified_k_fold = StratifiedKFold(n_splits = 10)

	classifier = GridSearchCV(DecisionTreeClassifier(), params, cv = stratified_k_fold, verbose = 5)
	classifier.fit(X_train, y_train)
	best_classifier = classifier.best_estimator_
	y_pred = best_classifier.predict(X_test)

	# model statistics
	print('Decision Trees Model Statistics')
	print('Best params: {0}'.format(classifier.best_params_))
	model_stats.compute_basic_stats(y_test, y_pred)
	model_stats.compute_roc_score(y_test, y_pred)
	model_stats.plot_normalized_confusion_matrix(
		y_test, y_pred, 'Decision Trees Classifier Normalized Confusion Matrix'
	)

	# fit the classifier on the complete dataset once we get best parameters
	best_classifier = DecisionTreeClassifier(**classifier.best_params_)
	best_classifier.fit(X, y)
	# save the model
	save_model(best_classifier, save_filepath)


if __name__ == '__main__':
	# stage 1
	learn_decision_tree(
		directories.stage_1_stratified_data_csv_file,
		os.path.join(directories.stage_1_saved_models, 'decision_tree.pkl')
	)
# stage 2
# learn_decision_tree(
# 	directories.stage_2_training_dataset_csv_file,
# 	os.path.join(directories.stage_2_saved_models, 'decision_tree.pkl')
# )
