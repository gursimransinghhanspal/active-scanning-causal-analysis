import numpy as np
import pandas as pd

required_features = [
	'ack.count',
	'ap.deauth.count',
	'beacon.count',
	'beacon.interval',
	'class3frames.count',
	'client.deauth.count',
	'frame.lossrate',
	'frames.persec',
	'ndf.count',
	'ssi.mean',
	'ssi.sd',
	'success.assoc.count'
]
label_column_name = 'label'


def read_labelled_csv_file(filepath, is_training: bool = True):
	if is_training:
		input_columns = list(required_features)
		input_columns.append(label_column_name)

		dataframe = pd.read_csv(filepath, sep = ',', names = input_columns)
		dataframe = dataframe.fillna(0)
		features_x, target_y = np.array(dataframe[required_features]), np.array(dataframe[label_column_name])
		return features_x, target_y
	else:
		dataframe = pd.read_csv(filepath, sep = ',', names = required_features)
		dataframe = dataframe.fillna(0)
		features_x = np.array(dataframe[required_features])
		return features_x
