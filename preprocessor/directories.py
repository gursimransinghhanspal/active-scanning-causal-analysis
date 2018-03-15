import os

"""
This script contains the absolute references to all the files and directories used in the project.
Any change in project structure may break this script. Beware!
"""

# these names are used to find reference to the sub-project root
__PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))


__CAPTURE_FILES_DIRNAME = 'capture_files'
__FRAMES_CSV_FILES_DIRNAME = 'frames_csv_files'
__SEMI_PROCESSED_FRAMES_CSV_FILES_DIRNAME = 'semi_processed_frames_csv_files'
__PROCESSED_EPISODE_CSV_FILES_DIRNAME = 'processed_episode_csv_files'
__TEMPORARY_FILES_DIRNAME = 'temporary'

# references to the directories
project = os.path.abspath(__PROJECT_DIR)

capture_files = os.path.join(__PROJECT_DIR, __CAPTURE_FILES_DIRNAME)
frames_csv_files = os.path.join(__PROJECT_DIR, __FRAMES_CSV_FILES_DIRNAME)
semi_processed_frames_csv_files = os.path.join(__PROJECT_DIR, __SEMI_PROCESSED_FRAMES_CSV_FILES_DIRNAME)
processed_episode_csv_files = os.path.join(__PROJECT_DIR, __PROCESSED_EPISODE_CSV_FILES_DIRNAME)
temporary = os.path.join(__PROJECT_DIR, __TEMPORARY_FILES_DIRNAME)

# misc
capture_files_extensions = ['.cap', '.pcap', '.pcapng', ]
csv_files_extensions = ['.csv', ]
conversion_mapping_file = os.path.join(__PROJECT_DIR, 'conversion_mapping.csv')
