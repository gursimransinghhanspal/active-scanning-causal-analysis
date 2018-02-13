import pandas as pd


def read_processed_csv_file(filepath, error_bad_lines: bool = False, warn_bad_lines: bool = True):
	"""
		Read processed csv file using `pandas` and convert it to a `dataframe`.
		Applies filters and other optimizations while reading to sanitize the data as much as possible.

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
		na_values = ['', ],  # values to consider as `not available`
		na_filter = True,  # detect `not available` values
		skip_blank_lines = True,  # skip any blank lines in the file
		float_precision = 'high',
		error_bad_lines = error_bad_lines,
		warn_bad_lines = warn_bad_lines
	)
	return csv_dataframe
