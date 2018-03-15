import os

from machine_learning.aux import constants, directories
from machine_learning.aux.constants import get_processed_data_file_header_segregation, get_dataset_label_header
from machine_learning.aux.helpers import read_csv_file
from machine_learning.preprocessing.classifier_stage_1.prepare_dataset import merge_and_label_processed_csv_files


def get_training_labels():
	"""
	Mapping from as-causes to training labels for stage 1 classifier

	Labels ->   0, APSP
				1, BL
				2, CE
				3, DFL
				4, LRSSI
				5, PWR_STATE
				6, ASSOC_PSCAN
				7, UNASSOC_PSCAN
	"""

	mapping = dict()
	mapping[constants.ASCause.apsp] = 0
	mapping[constants.ASCause.bl] = 1
	mapping[constants.ASCause.ce] = 2
	mapping[constants.ASCause.dfl] = 3
	mapping[constants.ASCause.lrssi] = 4
	mapping[constants.ASCause.pscan_assoc] = 6
	mapping[constants.ASCause.pscan_unassoc] = 7
	mapping[constants.ASCause.pwr_state] = 5
	return mapping


def add_column_to_csv(infile, outfile, col_name, col_value):
	"""
	Adds a column to given csv with same value over all rows
	"""

	infile = os.path.abspath(infile)
	outfile = os.path.abspath(outfile)

	in_dataframe = read_csv_file(infile)
	in_dataframe[col_name] = col_value

	head_features, head_training, head_properties = get_processed_data_file_header_segregation(for_training = True)
	req_columns = head_features + head_properties + head_training
	req_columns.append(col_name)

	in_dataframe.to_csv(outfile, mode = 'w', columns = req_columns, header = True, index = False)


if __name__ == '__main__':
	_f1 = os.path.join(directories.data_cluster, 'rw_temp.csv')
	_f2 = os.path.join(directories.data_cluster, 'realworld.csv')

	merge_and_label_processed_csv_files(_f1, get_training_labels(), True)
	add_column_to_csv(_f1, _f2, get_dataset_label_header(), 2)
	pass
