import numpy as np
import pandas as pd

labelled_data_header = ['ack.count', 'ap.deauth.count', 'beacon.count', 'beacon.interval', 'cause',
                        'class3frames.count', 'client.deauth.count', 'duration.time', 'end.time',
                        'failure.assoc.count', 'frame.lossrate', 'frames.persec', 'ndf.count', 'ssi.mean',
                        'ssi.sd', 'start.time', 'success.assoc.count', 'label']
required_features = ['ack.count', 'ap.deauth.count', 'beacon.count', 'beacon.interval', 'class3frames.count',
                     'client.deauth.count', 'frame.lossrate', 'frames.persec', 'ndf.count', 'ssi.mean',
                     'ssi.sd', 'success.assoc.count']


def read_labelled_csv_file(filepath, is_training: bool = True):
	if is_training:
		dataframe = pd.read_csv(filepath, sep = ',', names = labelled_data_header)
		dataframe = dataframe.fillna(0)
		features_x, target_y = np.array(dataframe[required_features]), np.array(dataframe['label'])
		return features_x, target_y
	else:
		dataframe = pd.read_csv(filepath, sep = ',', names = labelled_data_header)
		dataframe = dataframe.fillna(0)
		features_x = np.array(dataframe[required_features])
		return features_x
