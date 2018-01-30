#!python3.6

import os
import subprocess

# the current directory
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
# the captured files directory
CAPTURE_FILES_DIR = os.path.join(PROJECT_DIR, 'capture_files')
# the raw csv files directory
RAW_CSV_DIR = os.path.join(PROJECT_DIR, 'raw_csv_files')

# Supported Extensions - only files with supported extensions shall be read
SUPPORTED_EXTS = ['.pcap', '.pcapng', '.cap', ]


def prepare_environment():
	# create directories if they don't exist
	if not os.path.exists(CAPTURE_FILES_DIR) or not os.path.isdir(CAPTURE_FILES_DIR):
		os.mkdir(CAPTURE_FILES_DIR)
	if not os.path.exists(RAW_CSV_DIR) or not os.path.isdir(RAW_CSV_DIR):
		os.mkdir(RAW_CSV_DIR)

	# make sure CAPTURE_FILES_DIR is not empty
	if len(os.listdir(CAPTURE_FILES_DIR)) == 0:
		print('"{:s}" is empty! Please add some capture files and try again!'.format(CAPTURE_FILES_DIR))
		exit(0)
	# make sure RAW_CSV_DIR is empty
	if len(os.listdir(RAW_CSV_DIR)) != 0:
		print('"{:s}" is not empty! Please empty the directory and try again!'.format(RAW_CSV_DIR))
		exit(0)


def prepare_and_get_command_format_string():
	"""
	Use Tshark to convert capture files to csv format.
	"""

	space = ' '
	command = 'tshark -E separator=, -T fields' + space + \
	          '-e frame.number' + space + \
	          '-e frame.time_epoch' + space + \
	          '-e frame.len' + space + \
	          '-e radiotap.channel.freq' + space + \
	          '-e radiotap.mactime' + space + \
	          '-e radiotap.datarate' + space + \
	          '-e wlan.fc.type_subtype' + space + \
	          '-e wlan_mgt.ssid' + space + \
	          '-e wlan.bssid' + space + \
	          '-e wlan_mgt.ds.current_channel' + space + \
	          '-e wlan_mgt.qbss.scount' + space + \
	          '-e wlan.fc.retry' + space + \
	          '-e wlan.fc.pwrmgt' + space + \
	          '-e wlan.fc.moredata' + space + \
	          '-e wlan.fc.frag' + space + \
	          '-e wlan.duration' + space + \
	          '-e wlan.ra' + space + \
	          '-e wlan.ta' + space + \
	          '-e wlan.sa' + space + \
	          '-e wlan.da' + space + \
	          '-e wlan.seq' + space + \
	          '-e wlan.qos.priority' + space + \
	          '-e wlan.qos.amsdupresent' + space + \
	          '-e wlan.fc.type' + space + \
	          '-e wlan_mgt.fixed.reason_code' + space + \
	          '-e wlan_mgt.fixed.status_code' + space + \
	          '-e wlan.fc.ds' + space + \
	          '-e radiotap.dbm_antsignal' + space + \
	          '-r ' + '\'{0}\' ' + '>> \'{1}\''
	return command


def prepare_and_get_csv_header(command_format_string: str):
	"""
	Create a csv header string for the csv files
	"""

	split_command = command_format_string.split(' ')

	# choose the elements which have `-e` as their previous element
	# i.e., choose the property names to be extracted from the capture file
	csv_header = list()
	for i in range(1, len(split_command)):
		if split_command[i - 1] == '-e':
			csv_header.append(split_command[i])

	# for some reason the last column is always duplicated in the output
	csv_header.append(csv_header[-1])

	# join the list to form a comma separated string. also add `newline` char
	csv_header_string = str.join(',', csv_header)
	csv_header_string += '\n'
	return csv_header_string


def get_capture_file_names():
	"""
	Read all the files present in the CAPTURE_FILES_DIR
	"""

	capture_file_names = list()
	for file in os.listdir(CAPTURE_FILES_DIR):
		if os.path.splitext(file)[1] in SUPPORTED_EXTS:
			capture_file_names.append(file)

	# sort so that we always read in a predefined order
	capture_file_names.sort()
	return capture_file_names


def generate_output_csv_files(capture_file_names: list, command_format_string: str, csv_file_header: str):
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
		capture_file = os.path.join(CAPTURE_FILES_DIR, capture_name)
		# csv file
		csv_file = os.path.join(RAW_CSV_DIR, csv_name)

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
		# os.waitpid(p.pid, 0)
		subprocesses.append(p)

	exit_codes = [q.wait() for q in subprocesses]
	# print the exit codes
	print('Exit codes for sub-processes: ', exit_codes)

	return exit_codes


def main():
	prepare_environment()
	command_format_string = prepare_and_get_command_format_string()
	csv_file_header = prepare_and_get_csv_header(command_format_string)
	capture_file_names = get_capture_file_names()
	generate_output_csv_files(capture_file_names, command_format_string, csv_file_header)


if __name__ == '__main__':
	main()
