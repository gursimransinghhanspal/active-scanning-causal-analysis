from time import sleep, time
from typing import List

from data_collection.util.directory_utility import delete_directory, initialize_directory_counter
from data_collection.util.hostapd_utility import kill_ap_abruptly, start_ap, stop_all_ap_processes
from data_collection.util.iface_utility import does_iface_exist, iface_dn
# a list of all sniffers with the channel they sniff on
# type: List[(int, str),]
from data_collection.util.tshark_utility import start_capture, stop_all_captures
from data_collection.util.wpa_utility import associate_sta, disassociate_all_sta
from data_collection.beacon_loss.env import *

# the directory name counter
# no need to change, gets initialized automatically
_DIR_NAME_COUNTER = 1


#
# ***** begin ***** #
#

def _prepare_environment() -> int:
	"""
	Does initial checks and some mundane setup to begin
	:return: the initial dir name counter value
	"""

	ok = True

	# *** do all interfaces exist ***
	all_ifaces = [iface for _, iface in SNIFFER_INTERFACES]
	all_ifaces.append(AP_INTERFACE)
	all_ifaces.extend(CLIENT_INTERFACES)

	print('Checking all interfaces:')
	for ifname in all_ifaces:
		if not does_iface_exist(ifname):
			print('• `{:s}` does not exist!'.format(ifname))
			ok = False
		else:
			print('• `{:s}` exists!'.format(ifname))
	print()

	# *** reset ***
	_reset(None)

	# *** create root_save_dir if does not exist ***
	os.makedirs(ROOT_SAVE_DIR_PATH, exist_ok = True)
	print()
	print()

	# *** status ***
	return ok


def _reset(save_dir_path):
	"""
	Resets the environment

	:param save_dir_path: if provided, deletes the directory... should be used when some error occurs
	:return:
	"""

	print("+" * 40)
	print("Resetting environment")
	print()

	if save_dir_path is not None:
		delete_directory(save_dir_path)

	# stop current ongoing capture
	stop_all_captures()
	# stop the ap process
	stop_all_ap_processes()
	# disassociate all clients
	disassociate_all_sta(CLIENT_INTERFACES)

	# turn off all interfaces
	# sniffers
	for _, ifname in SNIFFER_INTERFACES:
		iface_dn(ifname = ifname)
	# clients
	for ifname in CLIENT_INTERFACES:
		iface_dn(ifname = ifname)
	# access point
	iface_dn(AP_INTERFACE)

	print()
	print("+" * 40)
	print()


def _collect():
	"""
	Collects one episode per client
	"""

	global _DIR_NAME_COUNTER

	print('-' * 40)
	print('-' * 40)
	print('_collect(): Starting collection {:d}. [{:f}]'.format(_DIR_NAME_COUNTER, time()))

	_save_dir_path = os.path.join(ROOT_SAVE_DIR_PATH, str(_DIR_NAME_COUNTER))
	if os.path.exists(_save_dir_path):
		print('_collect(): Something has gone wrong! directory `{:s}` already exists'.format(str(_save_dir_path)))
		return False
	else:
		os.mkdir(_save_dir_path)

	# *** actual work starts here ***

	# start ap
	rc = start_ap(HOSTAPD_EXEC_PATH, HOSTAPD_CONF_PATH, AP_INTERFACE, AP_IP_ADDRESS, AP_NETMASK)
	if rc != 0:
		_reset(_save_dir_path)
		return
	print("." * 40)
	print()

	# give some time to start
	sleep(10)

	# associate clients
	# - associate each client to the ap with a sleep time of 5s in between
	#   - gives ample time to complete the handshake
	#   - reduces frame collision between multiple clients
	for ifname in CLIENT_INTERFACES:
		_ok = associate_sta(ifname, WPA_SUPPLICANT_CONF_PATH, assert_association = True)
		sleep(5)
		if not _ok:
			_reset(_save_dir_path)
			return
	print("." * 40)
	print()

	# buffer before sniffing (to let all the connection establishment episodes occur)
	sleep(10)

	# start sniffing
	for channel, ifname in SNIFFER_INTERFACES:
		rc = start_capture(ifname, channel, _DIR_NAME_COUNTER, _save_dir_path)
		if rc != 0:
			_reset(_save_dir_path)
			return
	print("." * 40)
	print()

	# buffer time to populate pcapng file
	sleep(30)

	# turn down ap iface
	rc = kill_ap_abruptly(AP_INTERFACE)
	if rc != 0:
		_reset(_save_dir_path)
		return
	print("." * 40)
	print()

	# buffer time to populate pcapng file
	sleep(30)

	# stop current ongoing capture
	stop_all_captures()
	# stop the ap process
	stop_all_ap_processes()
	# disassociate all clients
	disassociate_all_sta(CLIENT_INTERFACES)

	# turn off all interfaces
	# sniffers
	for _, ifname in SNIFFER_INTERFACES:
		iface_dn(ifname = ifname)
	# clients
	for ifname in CLIENT_INTERFACES:
		iface_dn(ifname = ifname)
	# access point
	iface_dn(AP_INTERFACE)

	# update counter
	_DIR_NAME_COUNTER += 1

	print()
	print("_collect(): Completed collection of one episode per client. [{:f}]".format(time()))
	print('-' * 40)
	print('-' * 40)
	print()
	return True


def main():
	ok = _prepare_environment()

	# initialize the dir name counter
	global _DIR_NAME_COUNTER
	_DIR_NAME_COUNTER = initialize_directory_counter(ROOT_SAVE_DIR_PATH)

	while ok:
		ok = _collect()
		# buffer time between collections
		sleep(10)

		# always collect
		# comment the following statement to stop the script when a collection attempt fails
		ok = True


if __name__ == "__main__":
	main()
