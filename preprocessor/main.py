"""
The controller file...
	Following operations can be performed:
		1. `cap`, `pcap` or `pcapng` (or similar formats) can be converted to csv format -- frame csv file
			Headers extracted:
				'frame.number'
				'frame.time_epoch'
				'frame.len'
				'wlan.duration'
				'-e wlan.bssid'
				'-e wlan.ra'
				'-e wlan.ta'
				'-e wlan.sa'
				'-e wlan.da'
				'-e wlan.seq'
				'-e wlan_mgt.ssid'
				'-e wlan_mgt.ds.current_channel'
				'-e wlan_mgt.qbss.scount'
				'-e wlan_mgt.fixed.reason_code'
				'-e wlan_mgt.fixed.status_code'
				'-e wlan.fc.type'
				'-e wlan.fc.type_subtype'
				'-e wlan.fc.retry'
				'-e wlan.fc.pwrmgt'
				'-e wlan.fc.moredata'
				'-e wlan.fc.frag'
				'-e wlan.fc.ds'
				'-e wlan.qos.priority'
				'-e wlan.qos.amsdupresent'
				'-e radiotap.channel.freq'
				'-e radiotap.mactime'
				'-e radiotap.datarate'
				'-e radiotap.dbm_antsignal'

		2. convert frame csv files to episode characteristics csv files
			calculates various characteristics by analyzing a frames csv
			slices the frames into episodes

		3. tag with active scanning causes according to the old rule based system

		4. merge given csv files into one... (maintenance feature)
"""

import argparse


def define_command_line_parser():
	"""
	Defines a simple argument parser for the script
	"""

	# the parser
	arg_parser = argparse.ArgumentParser()

	# - action
	arg_parser.add_argument(
		'-a', '--action',
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


def get_command_line_arguments():
	pass


def process_and_execute_commands():
	pass


if __name__ == '__main__':
	pass
