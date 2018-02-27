import os

"""
This script contains the absolute references to all the files and directories used in the project.
Any change in project structure may break this script. Beware!
"""

# these names are used to find reference to the sub-project root
__PROJECT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

__PROCESSED_FILES_DIR_NAME = 'processed_csv_files'
__PROCESSED_FILES_TRAINING_DIR_NAME = 'training'
__PROCESSED_FILES_TESTING_DIR_NAME = 'testing'
__TRAINING_CAUSE_APSP_DIR_NAME = 'ap_side_procedures'
__TRAINING_CAUSE_BL_DIR_NAME = 'beacon_loss'
__TRAINING_CAUSE_CE_DIR_NAME = 'connection_establishment'
__TRAINING_CAUSE_DFL_DIR_NAME = 'data_frame_loss'
__TRAINING_CAUSE_LRSSI_DIR_NAME = 'low_rssi'
__TRAINING_CAUSE_PSCAN_ASSOC_DIR_NAME = 'periodic_scan_associated'
__TRAINING_CAUSE_PSCAN_UNASSOC_DIR_NAME = 'periodic_scan_unassociated'
__TRAINING_CAUSE_PWR_STATE_DIR_NAME = 'power_state_low_to_high'

__DATA_DIR_NAME = 'data'
__DATA_STAGE_1_DIR_NAME = 'stage_1'
__DATA_STAGE_2_DIR_NAME = 'stage_2'
__LABELED_DATA_CSV_FILE_NAME = 'labeled_data.csv'
__UNLABELED_DATA_CSV_FILE_NAME = 'unlabeled_data.csv'
__STRATIFIED_DATA_CSV_FILE_NAME = 'stratified_data.csv'

__SAVED_MODEL_DIR_NAME = 'saved_models'
__STAGE_1_SAVED_MODEL_DIR_NAME = 'stage_1'
__STAGE_2_SAVED_MODEL_DIR_NAME = 'stage_2'

__TEMPORARY_DIR_NAME = 'temporary'

# references to the directories
project = os.path.abspath(__PROJECT_DIR)

processed_files = os.path.join(project, __PROCESSED_FILES_DIR_NAME)
processed_files_training = os.path.join(processed_files, __PROCESSED_FILES_TRAINING_DIR_NAME)
processed_files_testing = os.path.join(processed_files, __PROCESSED_FILES_TESTING_DIR_NAME)
training_cause_apsp = os.path.join(processed_files_training, __TRAINING_CAUSE_APSP_DIR_NAME)
training_cause_bl = os.path.join(processed_files_training, __TRAINING_CAUSE_BL_DIR_NAME)
training_cause_ce = os.path.join(processed_files_training, __TRAINING_CAUSE_CE_DIR_NAME)
training_cause_dfl = os.path.join(processed_files_training, __TRAINING_CAUSE_DFL_DIR_NAME)
training_cause_lrssi = os.path.join(processed_files_training, __TRAINING_CAUSE_LRSSI_DIR_NAME)
training_cause_pscan_assoc = os.path.join(processed_files_training, __TRAINING_CAUSE_PSCAN_ASSOC_DIR_NAME)
training_cause_pscan_unassoc = os.path.join(processed_files_training, __TRAINING_CAUSE_PSCAN_UNASSOC_DIR_NAME)
training_cause_pwr_state = os.path.join(processed_files_training, __TRAINING_CAUSE_PWR_STATE_DIR_NAME)

data = os.path.join(project, __DATA_DIR_NAME)
data_stage_1 = os.path.join(data, __DATA_STAGE_1_DIR_NAME)
data_stage_2 = os.path.join(data, __DATA_STAGE_2_DIR_NAME)
stage_1_unlabeled_data_csv_file = os.path.join(data_stage_1, __UNLABELED_DATA_CSV_FILE_NAME)
stage_1_labeled_data_csv_file = os.path.join(data_stage_1, __LABELED_DATA_CSV_FILE_NAME)
stage_1_stratified_data_csv_file = os.path.join(data_stage_1, __STRATIFIED_DATA_CSV_FILE_NAME)
stage_2_unlabeled_data_csv_file = os.path.join(data_stage_2, __UNLABELED_DATA_CSV_FILE_NAME)
stage_2_merged_dataset_csv_file = os.path.join(data_stage_2, __LABELED_DATA_CSV_FILE_NAME)
stage_2_training_dataset_csv_file = os.path.join(data_stage_2, __STRATIFIED_DATA_CSV_FILE_NAME)

saved_models = os.path.join(project, __SAVED_MODEL_DIR_NAME)
stage_1_saved_models = os.path.join(saved_models, __STAGE_1_SAVED_MODEL_DIR_NAME)
stage_2_saved_models = os.path.join(saved_models, __STAGE_2_SAVED_MODEL_DIR_NAME)

temporary = os.path.join(project, __TEMPORARY_DIR_NAME)


def create_directory(directory):
	"""
	Creates the given directory.
	"""

	abs_directory = os.path.abspath(directory)

	# if the directory doesn't exist, create the directory
	if not os.path.exists(abs_directory):
		os.mkdir(abs_directory)


def empty_directory(directory):
	"""
	Deletes and recreates the given directory.
	"""

	abs_directory = os.path.abspath(directory)
	delete_directory(abs_directory)

	# check if the directory is deleted, create the directory
	if not os.path.exists(abs_directory):
		os.mkdir(abs_directory)


def delete_directory(directory):
	"""
	Deletes the given directory
	"""

	abs_directory = os.path.abspath(directory)

	if not os.path.exists(abs_directory) or not os.path.isdir(abs_directory):
		return

	# delete the directory
	from shutil import rmtree
	rmtree(abs_directory)


def delete_file(filepath):
	"""
	Deletes the given file
	"""

	abs_path = os.path.abspath(filepath)
	if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
		return
	os.remove(abs_path)
