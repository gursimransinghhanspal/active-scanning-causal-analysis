import os

from machine_learning.aux import constants


def get_training_labels():
	"""
	Mapping from as-causes to training labels for stage 1 classifier

	Labels ->   0, if periodic scan unassociated
				1, if periodic scan associated
				2, if any other cause
	"""

	mapping = dict()
	mapping[constants.ASCause.apsp] = 2
	mapping[constants.ASCause.bl] = 2
	mapping[constants.ASCause.ce] = 2
	mapping[constants.ASCause.dfl] = 2
	mapping[constants.ASCause.lrssi] = 2
	mapping[constants.ASCause.pscan_assoc] = 1
	mapping[constants.ASCause.pscan_unassoc] = 0
	mapping[constants.ASCause.pwr_state] = 2
	return mapping





def get_training_label_proportions():
	"""
	Mapping from as-causes to training label proportions for stage 1 classifier
	"""

	mapping = dict()
	mapping[2] = 600
	mapping[1] = 100
	mapping[0] = 100
	return mapping


# dataframe = pd.DataFrame(data = X_final, columns = header)
# dataframe.to_csv(outfile, sep = ',', columns = header, header = True, index = False, mode = 'w')


if __name__ == '__main__':
	# merge_and_label_processed_csv_files(directories.stage_1_labeled_data_csv_file, get_training_labels(), True)
	# create_training_dataset(directories.stage_1_labeled_data_csv_file, directories.stage_1_stratified_data_csv_file,
	#                         None)
	pass
