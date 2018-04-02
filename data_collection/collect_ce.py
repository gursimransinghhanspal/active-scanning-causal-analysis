"""
A simple script to collect data for the cause `connection establishment`.

TIP: Since some commands require super user permissions and the script is intended to run for long periods
of time, prefer running in root shell (sudo su) so as to avoid sudo timeouts.

Steps:
	- start capture -- on channel 1, 6 and 11
	- wait 30 seconds
	- connect all specified clients to the access point
	- make sure all clients have connected properly,
		- if not, delete this capture session (fail-safe)
	- wait 30 seconds
	- stop the capture
	- disconnect all the clients

	- - - rinse and repeat - - -
"""

import os
from random import shuffle
from shutil import rmtree
from subprocess import DEVNULL
from time import sleep, time

from data_collection.aux import run_shell
from data_collection.monitor_mode import switch_to_monitor_mode

# #############################################################################
# ### Required info (arguments) ###
# #############################################################################

# wpa_supplicant.conf file
#   - should have the `ssid`, `passphrase` generated using wpa_passphrase command
#   - also include the `bssid`
# sample file:
__WPA_CONF = os.path.abspath(__file__)

# list of client device interfaces
__CLIENT_IFACE = [
	'',
]

# immutable list of sniffer interfaces
__SNIFFER_IFACE = (
	(1, ''),
	(6, ''),
	(11, ''),
)

# data save directory
__SAVE_DIR = os.path.abspath('')

# #############################################################################
# ### Script ###
# #############################################################################

# counter for directory names
__CAPTURE_COUNTER = 0


def __client_iface_exists():
	"""
	A simple call to `iwconfig <iface>` tells if the client is connected or not
	"""

	connected = True
	iface_command_fmt = 'iwconfig {:s}'

	for iface in __CLIENT_IFACE:
		iface_command = iface_command_fmt.format(iface)
		shell_output = run_shell(iface_command)
		shell_output = str.strip(shell_output)

		if len(shell_output) == 0:
			connected = False
			print('`{:s}` not connected to the machine. Please check all devices are connected!'.format(iface))
		else:
			print('`{:s}` connected.'.format(iface))
	return connected


def __init_directory_name_counter():
	"""

	:return:
	"""

	global __CAPTURE_COUNTER

	ls = os.listdir(__SAVE_DIR)
	ls = [int(i) for i in ls]
	ls.sort()

	if len(ls) == 0:
		__CAPTURE_COUNTER = 1
	else:
		__CAPTURE_COUNTER = ls[-1] + 1
	pass


def __connect_client(ifname):
	"""

	:param ifname:
	:return:
	"""

	connect_command_fmt = 'wpa_supplicant -c {:s} -B -i {:s}'
	connect_command = connect_command_fmt.format(str(__WPA_CONF), ifname)
	run_shell(connect_command, output = DEVNULL)

	# wait till the client is connected OR 60 seconds have passed
	#   - check if the `Access Point` field in `iwconfig` output has a mac-address
	assert_connected_command_fmt = ('iwconfig {:s} | '
	                                'grep "Access Point" | '
	                                'awk \'{print match($0, "Access Point: ..:..:..:..:..:..")}\'')

	__sleep_time = 1
	__second_counter = 0
	while __second_counter < 60:
		sleep(__sleep_time)
		__second_counter += __sleep_time

		assert_connected_command = assert_connected_command_fmt.format(ifname)
		output = run_shell(assert_connected_command)
		output_str = str(output.stdout).strip()
		output_int = int(output_str)

		connected = output_int > 0
		if connected:
			print('{:s} connected to the AP -- [~ {:02d}s], epoch: {:f}'.format(ifname, __second_counter, time()))
			return True

	print('{:s} could not connect to the AP -- [~ {:02d}s], epoch: {:f}'.format(ifname, __second_counter, time()))
	return False


def __disconnect_clients():
	"""

	:return:
	"""

	global __CLIENT_IFACE

	disconnect_command = 'killall wpa_supplicant'
	while True:
		output = run_shell(disconnect_command)
		# ideally should stop in first try
		if output.returncode == 0:
			print('wpa_supplicant killed!, epoch: {:f}'.format(time()))
			break

	assert_disconnect_command_fmt = ('iwconfig {:s} | '
	                                 'grep "Access Point" | '
	                                 'awk \'{print match($0, "Access Point: ..:..:..:..:..:..")}\'')

	# wait till all the clients are disconnected
	#   - check if the `Access Point` field in `iwconfig` output do not have a mac-address
	for ifname in __CLIENT_IFACE:
		__sleep_time = 1
		__second_counter = 0
		while __second_counter < 60:
			sleep(__sleep_time)
			__second_counter += __sleep_time

			assert_disconnected_command = assert_disconnect_command_fmt.format(ifname)
			output = run_shell(assert_disconnected_command)
			output_str = str(output.stdout).strip()
			output_int = int(output_str)

			disconnected = output_int == 0
			if disconnected:
				print('{:s} disconnected from the AP -- [~ {:02d}s], epoch: {:f}'.format(ifname, __second_counter,
				                                                                         time()))
				break


def prepare():
	"""

	:return:
	"""

	global __SNIFFER_IFACE

	# all client iface must exist
	if not __client_iface_exists():
		return

	# save directory must exist
	if not os.path.exists(__SAVE_DIR):
		return

	# initialize dirname counter
	__init_directory_name_counter()

	# switch sniffers
	for ch, iface in __SNIFFER_IFACE:
		switch_to_monitor_mode(iface, ch)

	pass


def collect():
	"""
	Collects one episode for connection establishment cause
	:return:
	"""

	global __SAVE_DIR
	global __CAPTURE_COUNTER
	global __SNIFFER_IFACE
	global __CLIENT_IFACE

	print('-' * 40)
	print('Starting capture {:d}, epoch: {:f}'.format(__CAPTURE_COUNTER, time()))

	# make sure directory doesn't exist already
	_dirname = os.path.join(__SAVE_DIR + str(__CAPTURE_COUNTER))
	if os.path.exists(_dirname):
		print('Something has gone wrong! directory `{:d}/` already exists'.format(__CAPTURE_COUNTER))
		return False

	# create directory
	os.mkdir(_dirname)

	# begin capture on all specified channels
	start_capture_command_fmt = 'tshark -i {:s} -w {:s} &'
	filename_fmt = 'control_ce_{:05d}_ch{:02d}.pcapng'
	for ch, ifname in __SNIFFER_IFACE:
		filename = filename_fmt.format(__CAPTURE_COUNTER, ch)
		file = os.path.join(_dirname, filename)
		start_capture_command = start_capture_command_fmt.format(ifname, str(file))
		run_shell(start_capture_command, output = DEVNULL)
		print('capture started on channel {:d} using iface {:s}, epoch: {:f}'.format(ch, ifname, time()))

	# wait 30 seconds
	sleep(30)

	# shuffle list to randomize connection order (unnecessary)
	shuffle(__CLIENT_IFACE)
	# connect each client to the ap with a sleep time of 10s in between
	#   - gives ample time to complete the handshake
	#   - reduces data frame loss between multiple clients
	for ifname in __CLIENT_IFACE:
		_ok = __connect_client(ifname)
		if not _ok:
			# potential infinite loop if client can not connect!
			rmtree(_dirname)
			return True
		sleep(10)

	# wait 30 seconds
	sleep(30)

	# stop capture
	stop_capture_command = 'killall tshark'
	while True:
		output = run_shell(stop_capture_command)
		# ideally should stop in first try
		if output.returncode == 0:
			print('capture completed!, epoch: {:f}'.format(time()))
			break

	# disconnect all the clients
	__disconnect_clients()

	# increment capture counter
	__CAPTURE_COUNTER += 1

	print('-' * 40)
	return True


if __name__ == '__main__':
	# prepare environment
	prepare()

	# start collection
	ok = True
	while ok:
		ok = collect()

	pass
