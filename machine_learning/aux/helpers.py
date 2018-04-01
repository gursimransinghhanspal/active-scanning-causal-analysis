import numpy as np
import pandas as pd

from machine_learning.aux.constants import get_training_label_header


def read_csv_file(filepath, error_bad_lines: bool = False, warn_bad_lines: bool = True):
	"""
	Read csv file using `pandas` and convert it to a `dataframe`.

	:param filepath: path to the csv file
	:param error_bad_lines: raise an error for malformed csv line (False = drop bad lines)
	:param warn_bad_lines: raise a warning for malformed csv line (only if `error_bad_lines` is False)
	:return: dataframe object
	"""

	csv_dataframe = pd.read_csv(
		filepath_or_buffer = filepath,
		sep = ',',  # comma separated values (default)
		header = 0,  # use first row as column_names
		index_col = None,  # do not use any column to index
		skipinitialspace = True,  # skip any space after delimiter
		na_filter = True,  # detect `not available` values
		skip_blank_lines = True,  # skip any blank lines in the file
		float_precision = 'high',
		error_bad_lines = error_bad_lines,
		warn_bad_lines = warn_bad_lines
	)
	return csv_dataframe


def read_dataset_csv_file_as_np_arrays(filepath, features, for_training: bool):
	"""
	Read a dataset csv file.

	:param filepath:
	:param for_training: if True, expects a `label` column to exist in the file.
	:return:
	"""

	dataframe = read_csv_file(filepath)

	if for_training:
		# feature_set, target_set, extra_properties = get_processed_data_file_header_segregation(for_training = True)

		features_x = np.array(dataframe[features])
		target_y = np.array(dataframe[get_training_label_header()])
		# extra_z = np.array(dataframe[extra_properties])

		target_y = np.reshape(target_y, target_y.shape[0])
		return features_x, target_y
	else:
		# feature_set, extra_properties = get_processed_data_file_header_segregation(for_training = False)

		features_x = np.array(dataframe[features])
		# extra_z = np.array(dataframe[extra_properties])
		return features_x
