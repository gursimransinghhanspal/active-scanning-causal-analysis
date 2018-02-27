import argparse
import os

import matplotlib.pyplot as plt
import numpy
import pandas

# @author: Gursimran Singh

# directories
DIR_NAME = os.path.dirname(os.path.abspath(__file__))
CSVs_DIR_NAME = 'converted_pcaps'
CSV_DIR = os.path.join(DIR_NAME, CSVs_DIR_NAME)
PLOTs_DIR_NAME = 'plotted_graphs'
PLOT_DIR = os.path.join(DIR_NAME, PLOTs_DIR_NAME)


def create_argument_parser():
	"""
	Creates and sets up a fairly simple argument parser for the script.
	:return: arg-parser
	"""

	arg_parser = argparse.ArgumentParser()

	arg_parser.add_argument(
		'-p', '--pcap',
		action = 'store',
		dest = 'pcap',
		required = True,
		help = 'Path to `pcap` file.'
	)
	arg_parser.add_argument(
		'-c', '--clients',
		action = 'store',
		dest = 'clients',
		required = True,
		help = 'MAC addresses of clients to filter out. aa:bb:cc:dd:ee:ff [, gg:hh:ii:jj:kk:ll ...]'
	)
	arg_parser.add_argument(
		'--save_plots',
		action = 'store_true',
		dest = 'should_save_plots',
		help = 'include to save plots'
	)
	return arg_parser


def convert_pcap_to_csv(filepath: str):
	"""
	Converts the given pcap file to a csv format file using `tshark`.
	Stores only the probe requests.
	:param filepath: pcap filepath
	:return:
	"""

	full_path = os.path.abspath(filepath)
	if not os.path.exists(full_path):
		raise ValueError('Provided pcap does not exist!')

	sys_command = 'tshark '
	sys_command += '-r ' + str(full_path) + ' '
	sys_command += '-2 -R "wlan.fc.type_subtype == 4" '
	sys_command += '-E separator=, '
	sys_command += '-T fields -e frame.number -e frame.time_epoch -e wlan.sa '

	outfile = os.path.join(CSV_DIR, os.path.splitext(os.path.basename(filepath))[0] + '.csv')
	sys_command += '>> ' + outfile

	# create out-dir
	if not os.path.exists(CSV_DIR):
		os.mkdir(CSV_DIR)

	# write header
	file = open(outfile, 'w')
	file.write('frame number,frame epoch time,source address' '\n')
	file.close()

	# execute command
	os.system(sys_command)
	return outfile


def plot_graphs_from_csv_for_clients(filepath, clients: str, should_save_plots: bool):
	"""
	Reads a csv file and plots a graph of epoch time differences.
	:param should_save_plots:
	:param clients:
	:param filepath: csv filepath
	"""

	def strip(value: str):
		if not isinstance(value, str):
			return value

		try:
			return_value = value.strip(' ')
		except AttributeError:
			return value

		return return_value

	file_df = pandas.read_csv(filepath, sep = ',', header = 0, names = [
		'f_number', 'epoch', 'sa',
	], converters = {
		'f_number': strip,
		'epoch': strip,
		'sa': strip
	})

	clients = clients.strip(' \n').split(',')
	mac_addrs = [mac_addr.strip(' ').lower() for mac_addr in clients]

	for mac_addr in mac_addrs:
		boolean_filter = [addr.lower() == mac_addr for addr in file_df.sa]
		filtered_df = file_df[boolean_filter]

		y = [float(epoch) for epoch in filtered_df.epoch]
		y_diff = numpy.diff(y)

		figure = plt.figure()
		plt.plot(y_diff, label = mac_addr)
		plt.ylabel('epoch time difference (sec)')
		plt.xlabel('probe request count')
		plt.title('periodicity plot for ' + mac_addr)
		plt.show()

		if should_save_plots:
			if not os.path.exists(PLOT_DIR):
				os.mkdir(PLOT_DIR)

			plotfile = os.path.join(PLOT_DIR, os.path.splitext(os.path.basename(filepath))[0] + '.png')
			figure.savefig(plotfile)


if __name__ == "__main__":
	parser = create_argument_parser()
	args = parser.parse_args()

	csv_file = convert_pcap_to_csv(args.pcap)
	plot_graphs_from_csv_for_clients(csv_file, args.clients, args.should_save_plots)

# for help:
#   python3 periodicity_plotter.py -h

# example:
#   python3 periodicity_plotter.py --pcap pcaps/02-11_moto_e.pcapng --clients 80:6c:1b:68:a9:99 --save_plots
