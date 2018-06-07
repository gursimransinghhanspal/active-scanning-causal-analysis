import os
from random import shuffle
from time import time, sleep
from typing import List

from data_collection.aux.directory_utility import initialize_directory_counter, delete_directory
from data_collection.aux.hostapd_utility import start_ap, kill_ap_abruptly, stop_all_ap_processes
from data_collection.aux.iface_utility import does_iface_exist, iface_dn

# a list of all sniffers with the channel they sniff on
# type: List[(int, str),]
from data_collection.aux.tshark_utility import start_capture, stop_all_captures
from data_collection.aux.wpa_utility import associate_sta, disassociate_all_sta

_SNIFFER_INTERFACES = [
	(1, ""),
	(6, ""),
	(11, ""),
]

# access point interface
_AP_INTERFACE = ""

# a list of all clients
_CLIENT_INTERFACES = [
	"",
	"",
]

# the directory name counter
_DIR_NAME_COUNTER = 1

# path to root directory where to save capture files
_ROOT_SAVE_DIR_PATH = os.path.abspath('')

# path to wpa_supplicant conf file
_WPA_SUPPLICANT_CONF_PATH = os.path.abspath('')
# path to hostapd executable
_HOSTAPD_EXEC_PATH = os.path.abspath('')
# path to hostapd conf file
_HOSTAPD_CONF_PATH = os.path.abspath('')


#
# ***** begin ***** #
#

def _prepare_environment(sniffer_ifaces: list, ap_iface: str, client_ifaces: list, root_save_dir) -> int:
	"""
	Does initial checks and some mundane setup to begin
	:return: the initial dir name counter value
	"""

	ok = True

	# *** do all interfaces exist ***
	all_ifaces = [iface for _, iface in sniffer_ifaces]
	all_ifaces.append(ap_iface)
	all_ifaces.extend(client_ifaces)

	print('Checking all interfaces:')
	for ifname in all_ifaces:
		if not does_iface_exist(ifname):
			print('• `{:s}` does not exist!'.format(ifname))
			ok = False
		else:
			print('• `{:s}` exists!'.format(ifname))
	print()
	del all_ifaces

	# *** create root_save_dir if does not exist ***
	os.makedirs(root_save_dir, exist_ok = True)

	# *** status ***
	return ok


def _reset(save_dir_path):
	delete_directory(save_dir_path)
	stop_all_ap_processes()
	disassociate_all_sta(_CLIENT_INTERFACES)


def _collect():
	"""
	Collects one episode per client
	"""

	print('-' * 40)
	print('Starting collection {:d}, epoch: {:f}'.format(_DIR_NAME_COUNTER, time()))

	_save_dir_path = os.path.join(_ROOT_SAVE_DIR_PATH, str(_DIR_NAME_COUNTER))
	if os.path.exists(_save_dir_path):
		print('Something has gone wrong! directory `{:s}` already exists'.format(str(_save_dir_path)))
		return False
	else:
		os.mkdir(_save_dir_path)

	# *** actual work starts here ***

	# start ap
	start_ap(_HOSTAPD_EXEC_PATH, _HOSTAPD_CONF_PATH, _AP_INTERFACE)
	# give some time to start
	sleep(30)

	# associate clients
	# - associate each client to the ap with a sleep time of 5s in between
	#   - gives ample time to complete the handshake
	#   - reduces frame collision between multiple clients
	for ifname in _CLIENT_INTERFACES:
		_ok = associate_sta(ifname, _WPA_SUPPLICANT_CONF_PATH)
		sleep(5)
		if not _ok:
			_reset(_save_dir_path)
			return

	# start sniffing
	for channel, ifname in _SNIFFER_INTERFACES:
		start_capture(ifname, channel, _DIR_NAME_COUNTER, _save_dir_path)

	# buffer time to populate pcapng file
	sleep(30)
	# turn down ap iface
	kill_ap_abruptly(_AP_INTERFACE)
	# buffer time to populate pcapng file
	sleep(30)

	# stop sniffing
	stop_all_captures()
	# kill ap process
	stop_all_ap_processes()
	# disconnect / reset
	disassociate_all_sta(_CLIENT_INTERFACES)
	# update counter
	global _DIR_NAME_COUNTER
	_DIR_NAME_COUNTER += 1

	print('-' * 40)


def main():
	ok = _prepare_environment(
		_SNIFFER_INTERFACES, _AP_INTERFACE, _CLIENT_INTERFACES, _ROOT_SAVE_DIR_PATH
	)

	# initialize the dir name counter
	global _DIR_NAME_COUNTER
	_DIR_NAME_COUNTER = initialize_directory_counter(_ROOT_SAVE_DIR_PATH)

	while ok:
		ok = _collect()


if __name__ == "__main__":
	main()
