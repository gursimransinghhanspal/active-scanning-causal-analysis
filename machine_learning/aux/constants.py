import enum

from . import directories


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


def get_active_scanning_causes_as_list():
	"""
	Returns all active scanning causes as a list
	"""

	active_scanning_causes = [
		cause for cause in ASCause
	]
	# sort so the order remains same every time
	active_scanning_causes.sort(key = lambda k: k.name)
	return active_scanning_causes


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
