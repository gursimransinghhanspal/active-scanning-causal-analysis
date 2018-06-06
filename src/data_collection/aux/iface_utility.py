"""

"""
import subprocess

from data_collection.aux.shell_utility import execute_in_shell


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
	output = execute_in_shell(command, stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
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
	output = execute_in_shell(ifdn_command, stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
	err_string = str(output.stderr).strip()
	# print(err_string)
	return int(len(err_string) != 0)


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
	output = execute_in_shell(ifup_command, stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
	err_string = str(output.stderr).strip()
	# print(err_string)
	return int(len(err_string) != 0)


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
	output = execute_in_shell(mon_command, stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
	err_string = str(output.stderr).strip()
	# print(err_string)
	rc = int(len(err_string) != 0)
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
	mon_command_fmt = "sudo iwconfig {:s} channel {:d}"
	mon_command = mon_command_fmt.format(ifname, channel)
	# run the command,
	# look only at `stderr` stream
	output = execute_in_shell(mon_command, stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
	err_string = str(output.stderr).strip()
	# print(err_string)
	rc = int(len(err_string) != 0)
	if rc != 0:
		return 4

	return 0


if __name__ == "__main__":
	pass
