import subprocess
from time import sleep, time

from data_collection.aux.iface_utility import iface_dn, iface_up
from data_collection.aux.shell_utility import execute_in_shell


def associate_sta(ifname: str, wpa_conf_path, assert_association: bool = True) -> bool:
	"""
	Attempts to associate a STA (client device) to an Access Point
	"""

	# turn on the interface before associating
	iface_up(ifname = ifname)

	# execute association command
	associate_command_fmt = "sudo wpa_supplicant -c {:s} -B -i {:s}"
	associate_command = associate_command_fmt.format(str(wpa_conf_path), ifname)
	print("associate_sta(): associating STA - `{:s}`. [{:f}]".format(associate_command, time()))
	out = execute_in_shell(associate_command, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
	print("associate_sta(): rc = {:d}. [{:f}]".format(out.returncode, time()))

	# wait till the client is connected OR 60 seconds have passed
	# check if the `Access Point` field in `iwconfig` output has a mac-address
	def assert_associated_command_fmt(_ifname):
		return ('iwconfig {:s} | '.format(_ifname) +
		        'grep "Access Point" | '
		        'awk \'{print match($0, "Access Point: ..:..:..:..:..:..")}\'')

	if assert_association:
		__sleep_time = 1
		__second_counter = 0
		while __second_counter < 60:
			sleep(__sleep_time)
			__second_counter += __sleep_time

			assert_connected_command = assert_associated_command_fmt(ifname)
			output = execute_in_shell(assert_connected_command)
			output_str = str(output.stdout).strip()
			output_int = int(output_str)

			connected = output_int > 0
			if connected:
				print('associate_sta(): {:s} associated -- [~ {:02d}s]. [{:f}]'.format(ifname, __second_counter,
				                                                                       time()))
				return True

		print('associate_sta(): {:s} could not be associated -- [~ {:02d}s]. [{:f}]'.format(ifname, __second_counter,
		                                                                                    time()))
		return False

	return True


def disassociate_all_sta(sta_ifaces: list = None, assert_disassociation: bool = True):
	"""
	Kill all the wpa_supplicant processes
	"""

	disconnect_command = 'sudo killall wpa_supplicant'
	while True:
		print("disassociate_all_sta(): killing all wpa_supplicant processes - `{:s}`. [{:f}]"
		      .format(disconnect_command, time()))
		output = execute_in_shell(disconnect_command)
		# ideally should stop in first try
		if output.returncode == 0:
			print('disassociate_all_sta(): wpa_supplicant killed! [{:f}]'.format(time()))
			break

	# if nothing to do further, return
	if sta_ifaces is None:
		return

	def assert_disassociated_command_fmt(_ifname):
		return ('iwconfig {:s} | '.format(_ifname) +
		        'grep "Access Point" | '
		        'awk \'{print match($0, "Access Point: ..:..:..:..:..:..")}\'')

	if assert_disassociation:
		# wait till all the clients are disassociated
		#   - check if the `Access Point` field in `iwconfig` output does not have a mac-address
		for ifname in sta_ifaces:
			__sleep_time = 1
			__second_counter = 0
			while __second_counter < 60:
				sleep(__sleep_time)
				__second_counter += __sleep_time

				assert_disassociated_command = assert_disassociated_command_fmt(ifname)
				output = execute_in_shell(assert_disassociated_command)
				output_str = str(output.stdout).strip()
				output_int = int(output_str)

				disassociated = output_int == 0
				if disassociated:
					print('disassociate_all_sta(): {:s} disassociated -- [~ {:02d}s]. [{:f}]'.format(ifname,
					                                                                                 __second_counter,
					                                                                                 time()))
					break


if __name__ == "__main__":
	pass
