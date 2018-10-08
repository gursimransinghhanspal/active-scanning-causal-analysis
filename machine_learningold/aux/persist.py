import os
import uuid

from sklearn.externals import joblib

from machine_learning.aux import directories


def save_model(model, filepath):
	if os.path.exists(filepath):
		print('{:s} already exists, the model will be stored in `temporary` directory'.format(filepath))
		temporary_dir = directories.temporary
		filename = str(uuid.uuid4()) + '.pkl'
		filepath = os.path.join(temporary_dir, filename)

	# add extension .pkl doesn't exist
	if os.path.splitext(filepath)[1] != '.pkl':
		basename = os.path.splitext(os.path.basename(filepath))[0]
		dirname = os.path.dirname(filepath)
		basename += '.pkl'
		filepath = os.path.join(os.path.abspath(dirname), basename)

	joblib.dump(model, filepath)
	print('Model saved at {:s}'.format(filepath))


def load_model(filepath):
	if not os.path.exists(filepath):
		print('{:s} doesn\'t exist'.format(filepath))
		return
	return joblib.load(filepath)
