import itertools

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.preprocessing import label_binarize


def compute_basic_stats(y_true, y_pred):
	print('Precision Score: {0}'.format(precision_score(y_true, y_pred, average = None)))
	print('Recall Score: {0}'.format(recall_score(y_true, y_pred, average = None)))
	print('F1 Score: {0}'.format(f1_score(y_true, y_pred, average = None)))


def compute_roc_score(y_true, y_pred):
	n_labels = np.unique(y_true).shape[0]
	y_true_binarized_labels = label_binarize(y_true, classes = range(n_labels))
	y_pred_binarized_labels = label_binarize(y_pred, classes = range(n_labels))
	print('ROC AUC Score:')
	for i in range(n_labels):
		print('Class {0} v/s Rest: {1}'.format(i, roc_auc_score(
			y_true_binarized_labels[:, i], y_pred_binarized_labels[:, i], average = None)))


# Plot the normalized confusion matrix.
def plot_normalized_confusion_matrix(y_true, y_pred, plt_title):
	class_labels = np.unique(y_true)
	n_labels = class_labels.shape[0]
	conf_mat = confusion_matrix(y_true, y_pred).astype(float)
	print(conf_mat)
	# Normalize the confusion matrix.
	for idx in range(conf_mat.shape[0]):
		conf_mat[idx] /= np.sum(conf_mat[idx])
	plt.imshow(conf_mat, interpolation = 'nearest', cmap = plt.cm.Blues)
	plt.title(plt_title)
	plt.colorbar()
	tick_marks = np.arange(n_labels)
	plt.xticks(tick_marks, class_labels.astype(int))
	plt.yticks(tick_marks, class_labels.astype(int))
	plt.xlabel('Predicted Label')
	plt.ylabel('Actual Label')
	for x, y in itertools.product(range(conf_mat.shape[0]), range(conf_mat.shape[1])):
		plt.text(y, x, format(conf_mat[x, y], '0.2f'), horizontalalignment = 'center', color = 'k')
	plt.show()
