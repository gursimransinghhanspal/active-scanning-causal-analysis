import subprocess
from time import sleep, time

from data_collection.aux.shell_utility import execute_in_shell


def associate_sta(ifname: str, wpa_conf_path) -> bool:
	"""
	Attempts to connect a STA (client device) to an Access Point
	"""

	connect_command_fmt = "sudo wpa_supplicant -c {:s} -B -i {:s}"
	connect_command = connect_command_fmt.format(str(wpa_conf_path), ifname)
	execute_in_shell(connect_command, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

	# wait till the client is connected OR 60 seconds have passed
	# check if the `Access Point` field in `iwconfig` output has a mac-address
	def assert_connected_command_fmt(_ifname):
		return ('iwconfig {:s} | '.format(_ifname) +
		        'grep "Access Point" | '
		        'awk \'{print match($0, "Access Point: ..:..:..:..:..:..")}\'')

	__sleep_time = 1
	__second_counter = 0
	while __second_counter < 60:
		sleep(__sleep_time)
		__second_counter += __sleep_time

		assert_connected_command = assert_connected_command_fmt(ifname)
		output = execute_in_shell(assert_connected_command)
		output_str = str(output.stdout).strip()
		output_int = int(output_str)

		connected = output_int > 0
		if connected:
			print('`{:s}` associated -- [~ {:02d}s], epoch: {:f}'.format(ifname, __second_counter, time()))
			return True

	print('`{:s}` could not be associated -- [~ {:02d}s], epoch: {:f}'.format(ifname, __second_counter, time()))
	return False


def disassociate_all_sta(client_ifaces: list = None):
	"""
	Kill all the wpa_supplicant processes
	"""

	disconnect_command = 'sudo killall wpa_supplicant'
	while True:
		output = execute_in_shell(disconnect_command)
		# ideally should stop in first try
		if output.returncode == 0:
			print('wpa_supplicant killed!, epoch: {:f}'.format(time()))
			break

	# if nothing to verify, return
	if client_ifaces is None:
		return

	def assert_disconnect_command_fmt(_ifname):
		return ('iwconfig {:s} | '.format(_ifname) +
		        'grep "Access Point" | '
		        'awk \'{print match($0, "Access Point: ..:..:..:..:..:..")}\'')

	# wait till all the clients are disconnected
	#   - check if the `Access Point` field in `iwconfig` output does not have a mac-address
	for ifname in client_ifaces:
		__sleep_time = 1
		__second_counter = 0
		while __second_counter < 60:
			sleep(__sleep_time)
			__second_counter += __sleep_time

			assert_disconnected_command = assert_disconnect_command_fmt(ifname)
			output = execute_in_shell(assert_disconnected_command)
			output_str = str(output.stdout).strip()
			output_int = int(output_str)

			disconnected = output_int == 0
			if disconnected:
				print('`{:s}` disassociated -- [~ {:02d}s], epoch: {:f}'.format(ifname, __second_counter,
				                                                                time()))
				break


if __name__ == "__main__":
	pass
