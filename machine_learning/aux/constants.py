import enum

from machine_learning.aux import directories


# the identified active scanning causes
class ASCause(enum.Enum):
	apsp = 'ap_side_procedures'
	bl = 'beacon_loss'
	ce = 'connection_establishment'
	dfl = 'data_frame_loss'
	lrssi = 'low_rssi'
	pscan_assoc = 'periodic_scan_associated'
	pscan_unassoc = 'periodic_scan_unassociated'
	pwr_state = 'power_state_low_to_high'


# def get_active_scanning_causes_as_list():
# 	"""
# 	Returns all active scanning causes as a list
# 	"""
#
# 	active_scanning_causes = [
# 		cause for cause in ASCause
# 	]
# 	# sort so the order remains same every time
# 	active_scanning_causes.sort(key = lambda k: k.name)
# 	return active_scanning_causes


def get_training_data_directories():
	"""
	Mapping from as-causes to respective training data directories
	"""

	mapping = dict()
	mapping[ASCause.apsp] = directories.training_cause_apsp
	mapping[ASCause.bl] = directories.training_cause_bl
	mapping[ASCause.ce] = directories.training_cause_ce
	mapping[ASCause.dfl] = directories.training_cause_dfl
	mapping[ASCause.lrssi] = directories.training_cause_lrssi
	mapping[ASCause.pscan_assoc] = directories.training_cause_pscan_assoc
	mapping[ASCause.pscan_unassoc] = directories.training_cause_pscan_unassoc
	mapping[ASCause.pwr_state] = directories.training_cause_pwr_state
	return mapping


def get_processed_data_file_header_structure(for_training = False):
	"""
	Returns header names for columns in input processed data files
	TODO: make this common across data_processing
	"""

	from preprocessor.convert_frames_to_episodes import get_output_column_order

	header = get_output_column_order()
	if for_training:
		header.append(get_training_label_header())
	return header


def get_processed_data_file_header_segregation(for_training = False):
	"""
	Divides the data file into subsets
	1. ML feature set
	2. Label column (if for_training == true)
	3. Remaining columns
	"""

	from preprocessor.convert_frames_to_episodes import EpisodeFeatures, EpisodeProperties

	# the for_training label
	training_label = get_training_label_header()
	# the feature set
	features = [item.value for item in EpisodeFeatures]
	features.sort()
	# required properties
	properties = [
		EpisodeProperties.associated_client__mac.value,
	]

	if for_training:
		return features, [training_label, ], properties
	else:
		return features, properties


def get_required_header(for_training = False):
	header = get_processed_data_file_header_segregation(for_training)

	if for_training:
		head = header[0] + header[2] + header[1]
	else:
		head = header[0] + header[1]


def get_training_label_header():
	return 'training_label'


def get_cluster_label_header():
	return 'cluster_label'


def get_dataset_label_header():
	return 'dataset_label'


def get_training_data_file_prefix():
	return 'training_'


if __name__ == '__main__':
	print(get_processed_data_file_header_segregation(True))
