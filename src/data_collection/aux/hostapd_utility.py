import subprocess
from time import time, sleep

from data_collection.aux.iface_utility import iface_dn, iface_up
from data_collection.aux.shell_utility import execute_in_shell


def start_ap(hostapd_exec_path, hostapd_conf_path, hostapd_ifname: str):
	"""
	Start a hostapd process with the provided conf file
		- Turn on the interface
		- Run the hostapd command
	"""

	start_command_fmt = "sudo {:s} {:s} -B -i {:s}"
	start_command = start_command_fmt.format(str(hostapd_exec_path), str(hostapd_conf_path), hostapd_ifname)

	# turn on the interface
	iface_up(hostapd_ifname)
	# small buffer
	sleep(1)

	# execute the command
	# no output required
	print("start_ap(): starting an access point... `{:s}`. [{:f}]".format(start_command, time()))
	out = execute_in_shell(start_command, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
	print("start_ap(): rc = {:d}. [{:f}]".format(out.returncode, time()))


def kill_ap_abruptly(hostapd_ifname: str) -> int:
	"""
	To simulate the access point physically turning off, we will turn off the ap interface
	"""

	print("kill_ap_abruptly(): turning off the ap interface - {:s}. [{:f}]".format(hostapd_ifname, time()))
	return iface_dn(hostapd_ifname)


def stop_all_ap_processes():
	"""

	"""

	stop_command = 'sudo killall hostapd'
	while True:
		print("stop_all_ap_processes(): killing all hostapd processes - `{:s}`. [{:f}]".format(stop_command, time()))
		output = execute_in_shell(stop_command)
		# ideally should stop in first try
		if output.returncode == 0:
			print('stop_all_ap_processes(): hostapd killed! [:f]'.format(time()))
			break


if __name__ == "__main__":
	# start_ap('/home/gursimran/Downloads/hostapd-2.6/hostapd/hostapd',
	# '/home/gursimran/Downloads/hostapd-2.6/hostapd/hostapd.conf', 'wlx6470022a59f9')
	# stop_all_ap_processes()
	pass
