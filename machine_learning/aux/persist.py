from sklearn.externals import joblib


def save_classifier(_clf, _clf_name):
	joblib.dump(_clf, _clf_name + '.pkl')


def load_classifier(_clf_name):
	return joblib.load(_clf_name)
