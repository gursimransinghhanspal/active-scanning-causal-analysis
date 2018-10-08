import os

from machine_learning import classifier
from machine_learning.aux import directories
from machine_learning.aux.constants import ASCause
from machine_learning.aux.preprocessor import create_training_dataset, merge_and_label_processed_csv_files
from preprocessor.constants import MLFeatures, WindowMetrics


def training_labels(class0_cause: ASCause):
	"""
	Defines training label for each cause
	Returns a dictionary of type -> ASCause: int, maps active scanning causes to a label

	:param class0_cause: cause that is assigned label 0, all other causes are label 1
	"""

	mapping = dict()
	for _cause in ASCause:
		if _cause == class0_cause:
			mapping[_cause] = 0
		else:
			mapping[_cause] = 1
	return mapping


def training_classifiers():
	"""
	Defines what classifiers to train for each cause and the file names of the saved models
	Returns a dictionary of type -> ASCause: [(filename, function), ...],
	where function is a training function -- trains a model on given data
	"""

	all_classifiers = [
		# ('bagging', classifier.bagging.learn),
		('boosting', classifier.boosting.learn),
		# ('decision_tree', classifier.decision_tree.learn),
		# ('sgd', classifier.gradient_descent.learn),
		# ('knn', classifier.knn.learn),
		# ('linear_svm', classifier.linear_svm.learn),
		# ('logreg', classifier.logistic_regression.learn),
		# ('gaussian_nb', classifier.naive_bayes.learn),
		# ('random_forest', classifier.random_forest.learn),
		# ('rbf_svm', classifier.rbf_svm.learn),
		# ('voting_classifier', classifier.voting_classifier.learn),
	]

	mapping = dict()
	mapping[ASCause.apsp] = list(all_classifiers)
	mapping[ASCause.bl] = list(all_classifiers)
	mapping[ASCause.ce] = list(all_classifiers)
	mapping[ASCause.dfl] = list(all_classifiers)
	mapping[ASCause.lrssi] = list(all_classifiers)
	mapping[ASCause.pscan_assoc] = list(all_classifiers)
	mapping[ASCause.pscan_unassoc] = list(all_classifiers)
	mapping[ASCause.pwr_state] = list(all_classifiers)
	return mapping


def training_features():
	"""

	:return:
	"""

	mapping = dict()
	mapping[ASCause.apsp] = [
		WindowMetrics.ap_deauth_frames__count,
	]
	mapping[ASCause.bl] = [
		WindowMetrics.beacons_linear_slope__difference,
		WindowMetrics.max_consecutive_beacon_loss__count,
	]
	mapping[ASCause.ce] = [
		WindowMetrics.connection_frames__count,
	]
	mapping[ASCause.dfl] = [
		WindowMetrics.frames__loss_ratio,
		WindowMetrics.ack_to_data__ratio,
		WindowMetrics.datarate__slope,
	]
	mapping[ASCause.lrssi] = [
		WindowMetrics.rssi__mean,
		WindowMetrics.rssi__slope,
	]
	mapping[ASCause.pscan_assoc] = [
		WindowMetrics.frames__arrival_rate,
		WindowMetrics.pspoll__count,
		WindowMetrics.pwrmgt_cycle__count,
	]
	mapping[ASCause.pscan_unassoc] = [
		WindowMetrics.class_3_frames__count,
		WindowMetrics.client_associated__bool
	]
	mapping[ASCause.pwr_state] = [
		WindowMetrics.frames__arrival_rate,
		WindowMetrics.null_frames__ratio,
		WindowMetrics.pspoll__count,
	]

	for key, value in mapping.items():
		updated = [item.value for item in value if item in MLFeatures]
		mapping[key] = updated
	return mapping


def label_training_data(datadir):
	"""
	Creates different datasets with labeled training data for each of the labels
		- <label_name>_merged
		- <label_name>_training -- this is the training data

	:param datadir: Directory where all data will be saved
	:return:
	"""

	datadir = os.path.abspath(datadir)
	directories.empty_directory(datadir)

	merged_data_file_prefix = 'merged_'
	training_data_file_prefix = 'training_'

	datafiles = dict()
	for _cause in ASCause:
		merged_filename = merged_data_file_prefix + _cause.value + '.csv'
		training_filename = training_data_file_prefix + _cause.value + '.csv'
		merged_file = os.path.join(datadir, merged_filename)
		cause_features = training_features()
		training_file = os.path.join(datadir, training_filename)

		cause_labels = training_labels(_cause)
		merge_and_label_processed_csv_files(
			outfile = merged_file,
			training_labels = cause_labels,
			select_features = cause_features[_cause],
			should_label = True
		)

		ftypes = ['%.18e'] * len(cause_features[_cause])
		ftypes.append('%d')
		ftypes = ','.join(ftypes)

		create_training_dataset(
			infile = merged_file,
			outfile = training_file,
			select_features = cause_features[_cause],
			types = ftypes,
			proportions = None
		)
		datafiles[_cause] = training_file
		directories.delete_file(merged_file)

	return datafiles


def train(datafiles, outdir):
	"""
	Trains 8 models, one for each cause

	:param datafiles:
	:param outdir: Directory where each trained model shall be saved
	:return:
	"""

	outdir = os.path.abspath(outdir)
	# directories.empty_directory(outdir)

	training_clfs = training_classifiers()

	for _cause in ASCause:
		print('*' * 40)
		print('*' * 40)
		print('Starting cause: {:s}'.format(_cause.value))

		_clfs = training_clfs[_cause]

		cause_dir = os.path.join(outdir, _cause.value)
		if not os.path.exists(cause_dir):
			os.mkdir(cause_dir)

		training_data_infile = datafiles[_cause]

		for _clf_name, _clf_fn in _clfs:
			print('+' * 40)
			print('Training classifier: {:s}'.format(_clf_name))

			_clf_fn(
				training_data_infile = training_data_infile,
				trained_model_outfile = os.path.join(cause_dir, _clf_name + '.pkl'),
				display_metrics = True,
				gs_verbose = 0,
				n_jobs = 1
			)
			print('+' * 40)

		print('*' * 40)
		print('*' * 40)
		print()


if __name__ == '__main__':
	# files = label_training_data(
	# 	datadir = os.path.join(directories.data, 'multi_stage_clf')
	# )

	files = {
		ASCause.apsp: os.path.join(directories.data, 'multi_stage_clf', 'training_ap_side_procedures.csv'),
		ASCause.bl: os.path.join(directories.data, 'multi_stage_clf', 'training_beacon_loss.csv'),
		ASCause.ce: os.path.join(directories.data, 'multi_stage_clf', 'training_connection_establishment.csv'),
		ASCause.dfl: os.path.join(directories.data, 'multi_stage_clf', 'training_data_frame_loss.csv'),
		ASCause.lrssi: os.path.join(directories.data, 'multi_stage_clf', 'training_low_rssi.csv'),
		ASCause.pscan_assoc: os.path.join(directories.data, 'multi_stage_clf', 'training_periodic_scan_associated.csv'),
		ASCause.pscan_unassoc: os.path.join(directories.data, 'multi_stage_clf',
		                                    'training_periodic_scan_unassociated.csv'),
		ASCause.pwr_state: os.path.join(directories.data, 'multi_stage_clf', 'training_power_state_low_to_high.csv'),
	}
	train(
		datafiles = files,
		outdir = os.path.join(directories.saved_models, 'multi_stage_clf')
	)
