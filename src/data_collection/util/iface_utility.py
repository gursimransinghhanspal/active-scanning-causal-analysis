"""

"""
import subprocess
from time import time

from data_collection.util.shell_utility import execute_in_shell


def does_iface_exist(ifname: str) -> bool:
	"""
	Checks if the specified network interface exists
	uses: `iwconfig <ifname>`

	:param ifname: interface name
	:return: True if exists, else False
	"""

	# prepare the command to run
	command_fmt = "iwconfig {:s}"
	command = command_fmt.format(ifname)

	# run the command,
	# look only at `stderr` stream
	print("does_iface_exist(): checking interface - `{:s}`. [{:f}]".format(command, time()))
	output = execute_in_shell(command, stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
	print("does_iface_exist(): rc = {:d}. [{:f}]".format(output.returncode, time()))
	err_string = str(output.stderr).strip()
	# print(err_string)
	return len(err_string) == 0


def iface_dn(ifname: str) -> int:
	"""
	Turn the interface down
	uses: sudo ifconfig <ifname> down

	:return
		@code 0: ok
		@code 1: if_dn command failed
	"""

	# prepare the command to run
	ifdn_command_fmt = "sudo ifconfig {:s} down"
	ifdn_command = ifdn_command_fmt.format(ifname)

	# run the command,
	# look only at `stderr` stream
	print("iface_dn(): turning off interface - `{:s}`. [{:f}]".format(ifdn_command, time()))
	output = execute_in_shell(ifdn_command, stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
	print("iface_dn(): rc = {:d}. [{:f}]".format(output.returncode, time()))
	return output.returncode


def iface_up(ifname: str) -> int:
	"""
	Turn the interface up
	uses: sudo ifconfig <ifname> up

	:return
		@code 0: ok
		@code 1: if_up command failed
	"""

	# prepare the command to run
	ifup_command_fmt = "sudo ifconfig {:s} up"
	ifup_command = ifup_command_fmt.format(ifname)

	# run the command,
	# look only at `stderr` stream
	print("iface_up(): turning on interface - `{:s}`. [{:f}]".format(ifup_command, time()))
	output = execute_in_shell(ifup_command, stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
	print("iface_up(): rc = {:d}. [{:f}]".format(output.returncode, time()))
	return output.returncode


def iface_sniff(ifname: str, channel: int = None) -> int:
	"""
	Changes the interface mode to `monitor`
	And sets the interface channel to the specified channel (if given)

	:return
		@code 0: ok
		@code 1: iface_dn failed
		@code 2: monitor mode command failed
		@code 3: iface_up failed
		@code 3: channel command failed
	"""

	# turn interface down
	rc = iface_dn(ifname)
	if rc != 0:
		return 1

	# switch to monitor mode
	# prepare the command to run
	mon_command_fmt = "sudo iwconfig {:s} mode monitor"
	mon_command = mon_command_fmt.format(ifname)
	# run the command,
	# look only at `stderr` stream
	print("iface_sniff(): turning to monitor mode - `{:s}`. [{:f}]".format(mon_command, time()))
	output = execute_in_shell(mon_command, stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
	print("iface_sniff(): rc = {:d}. [{:f}]".format(output.returncode, time()))
	# print(err_string)
	rc = output.returncode
	if rc != 0:
		return 2

	# turn interface up
	rc = iface_up(ifname)
	if rc != 0:
		return 3

	if channel is None:
		return 0

	# switch to specified channel
	# prepare the command to run
	ch_command_fmt = "sudo iwconfig {:s} channel {:d}"
	ch_command = ch_command_fmt.format(ifname, channel)
	# run the command,
	# look only at `stderr` stream
	print("iface_sniff(): changing channel - `{:s}`. [{:f}]".format(ch_command, time()))
	output = execute_in_shell(ch_command, stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
	print("iface_sniff(): rc = {:d}. [{:f}]".format(output.returncode, time()))
	rc = output.returncode
	if rc != 0:
		return 4

	return 0


def iface_assign_ip(ifname: str, ip_addr: str, netmask: str):
	"""

	:param ifname:
	:param ip_addr:
	:param netmask:
	:return:
	"""

	# prepare the command to run
	ip_command_fmt = "sudo ifconfig {:s} {:s}/{:s}"
	ip_command = ip_command_fmt.format(ifname, ip_addr, netmask)
	# run the command,
	print("iface_assign_ip(): assigning ip - `{:s}`. [{:f}]".format(ip_command, time()))
	output = execute_in_shell(ip_command, stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
	print("iface_assign_ip(): rc = {:d}. [{:f}]".format(output.returncode, time()))
	rc = output.returncode
	if rc != 0:
		return 1
	return 0


if __name__ == "__main__":
	pass
