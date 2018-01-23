import numpy as np
import pandas as pd
import os

def get_training_data():
	dataframe = pd.read_csv(os.getcwd() + '/Dataset/AS_ML/as.csv', sep=',', header=0, index_col=0, engine='python')

	n_col = dataframe.shape[1]
	data = dataframe.as_matrix()[:, :n_col-1]
	target = dataframe.as_matrix()[:, n_col-1]

	target_names = np.array(['periodic', 'unknown', 'conn. est.', 'power management', 'beacon loss', 'ap-side', 'lowRSSI', 'frame loss'])
	features = np.array(['ack_count', 'ap_deauth_count', 'beacon_count', 'beacon_interval', 'cause', 'class3frames_count', 'client_deauth_count', 'duration_time', 'end_time', 'failure_assoc_count', 'frame_lossrate', 'frames_persec', 'ndf_count', 'ssi_mean', 'ssi_sd', 'start_time', 'success_assoc_count'])

	features_entities = {}

	for idx, feature in enumerate(features):

		if feature == 'cause':
			continue

		if type(data[0, idx]) is int or type(data[0, idx]) is float:
			n_unique_vals = len(np.unique(data[:, idx]))

			print ('----------------------')
			print ('Feature: %s' %feature)
			print ('Num unique values: %s' %n_unique_vals)

			if n_unique_vals > 100:
				n_unique_vals = 100

			min_feature_val = np.amin(data[:, idx])
			max_feature_val = np.amax(data[:, idx])

			print ('Min feature value: %s' %min_feature_val)
			print ('Max feature value: %s' %max_feature_val)
			print ('xxxxxxxxxxxxxxxxxxxxxx')

			features_entities[feature] = np.linspace(min_feature_val,
				max_feature_val, n_unique_vals + 1)

	training_data = {
		'data': data,
		'target': target,
		'features': features,
		'target_names': target_names,
		'features_entities': features_entities
	}

	return training_data
