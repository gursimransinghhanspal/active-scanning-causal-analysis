import os
import subprocess

from preprocessor import directories
from preprocessor.constants import FrameFields


def prepare_environment():
	# create directories if they don't exist
	if not os.path.exists(directories.capture_files) or not os.path.isdir(directories.capture_files):
		os.mkdir(directories.capture_files)
	if not os.path.exists(directories.frames_csv_files) or not os.path.isdir(directories.frames_csv_files):
		os.mkdir(directories.frames_csv_files)

	# make sure CAPTURE_FILES_DIR is not empty
	if len(os.listdir(directories.capture_files)) == 0:
		print('"{:s}" is empty! Please add some capture files and try again!'.format(directories.capture_files))
		exit(0)
	# make sure FRAMES_CSV_FILES_DIR is empty
	if len(os.listdir(directories.frames_csv_files)) != 0:
		print('"{:s}" is not empty! Please empty the directory and try again!'.format(directories.frames_csv_files))
		exit(0)


def prepare_and_get_command_format_string():
	"""
	Use Tshark to convert capture files to csv format.
	NOTE: use tshark version 2.2.13 for consistency

	`wlan_mgt.fixed.status_code` is not required for machine learning flow, but it is required only when assigning
	rbs tags for all the causes. Including it here since storage capacity is not a big concern.
	"""

	header_items = [item.value for item in FrameFields]

	command = 'tshark -E separator=, -T fields '
	for item in header_items:
		command += '-e ' + item + ' '
	command += '-r \'{0}\' >> \'{1}\''
	return command


def get_csv_header():
	"""
	Create a csv header string for the csv files
	"""

	header_items = [item.value for item in FrameFields]

	# for MIMO devices, radiotap.dbm_antsignal is itself a comma separated field
	# since handling this elegantly requires much more processing, we handle this by appending extra columns to
	# the csv file which would not be used mostly.
	# assuming MIMO 4x4 is the max (appending 4 extra headers [one for assurance])
	for i in range(4):
		header_items.append(FrameFields.radiotap_dbm_antsignal.value + '_' + str(i + 2))

	# join the list to form a comma separated string. also add `newline` char
	csv_header_string = str.join(',', header_items)
	csv_header_string += '\n'
	return csv_header_string


def get_capture_file_names():
	"""
	Read all the file names present in the CAPTURE_FILES_DIR
	"""

	capture_file_names = list()
	for file in os.listdir(directories.capture_files):
		if os.path.splitext(file)[1] in directories.capture_files_extensions:
			capture_file_names.append(file)

	# sort so that we always read in a predefined order
	# key: smallest file first
	capture_file_names.sort(key = lambda f: os.path.getsize(os.path.join(directories.capture_files, f)))
	return capture_file_names


def generate_output_csv_files(capture_file_names: list, command_format_string: str, csv_file_header: str,
                              use_subprocesses: bool = False):
	"""
	Run the command for each file name present in `capture_file_names` list
	"""

	subprocesses = list()
	for idx, capture_name in enumerate(capture_file_names):
		# base_name = capture_name without extension
		base_name = os.path.splitext(capture_name)[0]
		# csv_name = base_name + '.csv'
		csv_name = base_name + '.csv'

		# capture file
		capture_file = os.path.join(directories.capture_files, capture_name)
		# csv file
		csv_file = os.path.join(directories.frames_csv_files, csv_name)

		# print progress
		print('starting sub-process for file: {:s}...'.format(capture_name))

		# create csv file and add header as the first line
		with open(csv_file, 'w') as file:
			file.write(csv_file_header)
			file.close()

		# run command to append data to the csv file
		#   - this can be run in parallel
		command = command_format_string.format(str(capture_file), str(csv_file))
		p = subprocess.Popen(command, shell = True)

		if use_subprocesses:
			subprocesses.append(p)
		else:
			pid, exit_code = os.waitpid(p.pid, 0)
			print('Process pid {:d}, exit-code: {:d}:'.format(pid, exit_code))

	if use_subprocesses:
		exit_codes = [q.wait() for q in subprocesses]
		print('Exit codes for sub-processes: ', exit_codes)


def main():
	prepare_environment()
	command_format_string = prepare_and_get_command_format_string()
	csv_file_header = get_csv_header()
	capture_file_names = get_capture_file_names()
	generate_output_csv_files(capture_file_names, command_format_string, csv_file_header)


if __name__ == '__main__':
	main()
