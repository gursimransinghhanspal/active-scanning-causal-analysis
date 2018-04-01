import os

import numpy as np

from machine_learning.aux import constants, directories, helpers


def get_processed_csv_file_names(directory_path):
	"""
	Read all the file names present in the given directory
	"""
	__supported_extensions = ['.csv', ]

	processed_csv_file_names = list()

	listdir = os.listdir(directory_path)
	for file in listdir:
		if os.path.splitext(file)[1] in __supported_extensions:
			processed_csv_file_names.append(file)

	# sort so that we always read in a predefined order
	# key: smallest file first
	processed_csv_file_names.sort(key = lambda f: os.path.getsize(os.path.join(directory_path, f)))
	return processed_csv_file_names


def merge_and_label_processed_csv_files(outfile, training_labels, select_features = None, should_label: bool = True):
	"""
	Merges all the csv files in `processed_files` directory in a single csv file.
		- If `should_label` == True, then the training sub-directory is used and the data is also labeled
		  according to the folder the files are in.
		- Else, the testing subdirectory is used.
	"""

	def label_and_append_processed_csv_file(_filename, _write_filepath, required_columns, _cause = None):
		"""
		:param _filename:
		:param _write_filepath:
		:param required_columns:
		:param _cause:
		:return:
		"""

		_dataframe = helpers.read_csv_file(_filename)
		_dataframe = _dataframe[required_columns]
		_dataframe.dropna(inplace = True)

		if not os.path.exists(_write_filepath):
			_should_add_header = True
		else:
			_should_add_header = False

		header = list(required_columns)
		if _cause is not None:
			head_training = constants.get_training_label_header()
			_dataframe[head_training] = training_labels[_cause]
			header.append(head_training)

		_dataframe.to_csv(_write_filepath, mode = 'a', columns = header, header = _should_add_header,
		                  index = False)
		return _dataframe.shape[0]

	# required columns
	# used to choose only the required columns from the input processed episode csv
	if select_features is None:
		head_features, head_properties = constants.get_processed_data_file_header_segregation(for_training = False)
		req_columns = head_features + head_properties
	else:
		req_columns = select_features

	# count of number of instances
	instance_count = 0

	if should_label:
		# delete dataset files if they exist
		directories.delete_file(outfile)

		# get label info
		training_data_directories = constants.get_training_data_directories()

		# assign labels and merge
		for cause, directory in training_data_directories.items():
			if cause not in training_labels.keys():
				continue

			csv_filenames = get_processed_csv_file_names(directory)
			for filename in csv_filenames:
				csv_filename = os.path.abspath(os.path.join(directory, filename))
				instance_count += label_and_append_processed_csv_file(csv_filename, outfile,
				                                                      required_columns = req_columns, _cause = cause)

			print('• Total instance count for cause "{:s}":'.format(cause.name), instance_count)
			instance_count = 0
	else:
		# delete dataset files if they exist
		directories.delete_file(outfile)

		# get label info
		testing_data_directory = directories.processed_files_testing

		# merge
		csv_filenames = get_processed_csv_file_names(testing_data_directory)
		for filename in csv_filenames:
			csv_filename = os.path.abspath(os.path.join(testing_data_directory, filename))
			instance_count += label_and_append_processed_csv_file(csv_filename, outfile, required_columns = req_columns,
			                                                      _cause = None)

		print('• Total instance count:', instance_count)


def create_training_dataset(infile, outfile, select_features, types, proportions):
	"""
	Creates training dataset using the complete merged dataset file.
	"""

	X, y = helpers.read_dataset_csv_file_as_np_arrays(infile, select_features, for_training = True)
	print(np.bincount(y.astype(int)))

	# concatenate features and target
	X_temp = np.concatenate((X, np.vstack(y)), axis = 1)

	X_final = None

	# stratify if proportions are given
	if proportions is not None:
		for label, sample_size in proportions.items():
			X_label = X_temp[np.where(y == label)]
			if X_label.shape[0] == 0:
				continue

			# choose sample
			sample_size = min(X_label.shape[0], sample_size)
			X_label = X_label[np.random.choice(X_label.shape[0], sample_size, replace = False)]

			if X_final is None:
				X_final = np.array(X_label)
			else:
				X_final = np.append(X_final, X_label, axis = 0)
	else:
		X_final = X_temp

	if X_final is not None:
		# required columns (header)
		# head_features, head_training, _ = constants.get_processed_data_file_header_segregation(for_training = True)
		header = select_features
		header.append(constants.get_training_label_header())
		header_string = ','.join(header)

		# save array to outfile
		np.savetxt(
			outfile, X_final, delimiter = ',', header = header_string, comments = '',
			fmt = types
		)

# def identify_pscans_using_stage_1_classifier(infile, outfile, classifier_filepath, for_training):
# 	"""
# 	Removes periodic scan instances from the training dataset using stage 1 classifier
# 	"""
#
# 	def remove_unassociated_pscans(_dataframe, _pred):
# 		pass
#
# 	def remove_pscans(_dataframe, pred):
# 		# stage 1 training labels
# 		stage_1_training_labels = get_stage_1_training_labels()
#
# 		indexes_to_drop = list()
# 		for idx, label in enumerate(pred):
# 			if label == stage_1_training_labels[constants.ASCause.pscan_unassoc]:
# 				indexes_to_drop.append(idx)
#
# 		for idx, label in enumerate(pred):
# 			if label == stage_1_training_labels[constants.ASCause.pscan_assoc]:
# 				indexes_to_drop.append(idx)
#
# 		indexes_to_keep = set(range(_dataframe.shape[0])) - set(indexes_to_drop)
# 		return _dataframe.take(list(indexes_to_keep))
#
# 	infile = os.path.abspath(infile)
# 	outfile = os.path.abspath(outfile)
# 	classifier_filepath = os.path.abspath(classifier_filepath)
# 	classifier = load_model(classifier_filepath)
#
# 	# read the data to predict labels for
# 	features_x, _ = read_dataset_csv_file_as_np_arrays(filepath = infile, for_training = False)
# 	y_pred = classifier.predict(features_x)
#
# 	# some insight
# 	n_pred = y_pred.shape[0]
# 	print('• Periodic Scans prediction count: {}'.format(np.bincount(y_pred.astype(int))))
# 	print('• Periodic Scans prediction proportion: {}'.format(np.divide(np.bincount(y_pred.astype(int)), n_pred)))
#
# 	# read in the datafile
# 	dataframe = helpers.read_csv_file(infile)
# 	print('• Dataframe shape before dropping identified pscans:', dataframe.shape)
# 	# remove per_scans
# 	dataframe = remove_pscans(dataframe, y_pred)
# 	print('• Dataframe shape after dropping identified pscans:', dataframe.shape)
#
# 	# write the file back
# 	if for_training:
# 		head_features, head_training, head_properties = get_processed_data_file_header_segregation(for_training = True)
# 		header = head_features + head_properties + head_training
# 	else:
# 		head_features, head_properties = get_processed_data_file_header_segregation(for_training = False)
# 		header = head_features + head_properties
# 	dataframe.to_csv(outfile, columns = header, header = True, index = False, mode = 'w')


# def add_column_to_csv(infile, outfile, col_name, col_value):
# 	"""
# 	Adds a column to given csv with same value over all rows
# 	"""
#
# 	infile = os.path.abspath(infile)
# 	outfile = os.path.abspath(outfile)
#
# 	in_dataframe = read_csv_file(infile)
# 	in_dataframe[col_name] = col_value
#
# 	head_features, head_training, head_properties = get_processed_data_file_header_segregation(for_training = True)
# 	req_columns = head_features + head_properties + head_training
# 	req_columns.append(col_name)
#
# 	in_dataframe.to_csv(outfile, mode = 'w', columns = req_columns, header = True, index = False)
