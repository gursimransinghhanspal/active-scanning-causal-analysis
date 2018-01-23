from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

def plot_graph(data, target, feature, is_feature_val_cont,
				feature_entities, label, target_val):
	importance_dict = {entity: np.array([0, 0]) for entity in feature_entities}

	for datum_idx, datum in enumerate(data):
		if is_feature_val_cont:
			datum = feature_entities[np.argmin(np.abs(feature_entities - datum))]

		if target[datum_idx] == target_val:
			importance_dict[datum][0] += 1
		else:
			importance_dict[datum][1] += 1

	x = []
	xticks = []
	y_pred = []
	y_not_pred = []

	print (importance_dict)

	for entity in sorted(importance_dict):
		if is_feature_val_cont:
			x.append(entity)
		else:
			xticks.append(entity)

		n_pred = importance_dict[entity][0]
		n_not_pred = importance_dict[entity][1]

		if (n_pred == 0 and n_not_pred == 0):
			y_pred.append(0.0)
			y_not_pred.append(0.0)
		else:
			y_pred.append(n_pred / data.shape[0])
			y_not_pred.append(n_not_pred / data.shape[0])

	if not is_feature_val_cont:
		x = range(len(feature_entities))
		plt.xticks(x, xticks, rotation=45)

	plt.plot(x, y_pred, label='Label Predicted')
	plt.plot(x, y_not_pred, label='Label Not Predicted')
	plt.xlabel(feature)
	plt.ylabel('Prediction Probability')
	plt.title('%s v/s Prediction Count for label %s' %(feature, label))
	plt.legend(bbox_to_anchor=(0., 1.05, 1., .102), loc=3,
			ncol=2, mode="expand", borderaxespad=0.)
	plt.show()
