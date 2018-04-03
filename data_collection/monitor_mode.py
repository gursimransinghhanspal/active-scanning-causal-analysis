from data_collection.aux import run_shell


def turn_off_iface(ifname):
	"""

	:param ifname:
	:return:
	"""

	cmd_down = 'sudo ifconfig {:s} down'.format(ifname)
	shell_output = run_shell(cmd_down)
	stderr_str = str(shell_output.stderr).strip()
	if len(stderr_str) > 0:
		print('Could not turn off `{:s}`'.format(ifname))
		return False

	print('Turned off `{:s}`'.format(ifname))
	return True


def turn_on_iface(ifname):
	"""

	:param ifname:
	:return:
	"""

	cmd_up = 'sudo ifconfig {:s} up'.format(ifname)
	shell_output = run_shell(cmd_up)
	stderr_str = str(shell_output.stderr).strip()
	if len(stderr_str) > 0:
		print('Could not turn on `{:s}`'.format(ifname))
		return False

	print('Turned on `{:s}`'.format(ifname))
	return True


def switch_to_monitor_mode(ifname, channel: int = None):
	"""

	:param ifname:
	:param channel:
	:return:
	"""

	cmd_monitor = 'sudo iwconfig {:s} mode monitor'.format(ifname)

	turn_off_iface(ifname)

	shell_output = run_shell(cmd_monitor)
	stderr_str = str(shell_output.stderr).strip()
	if len(stderr_str) > 0:
		print('Could not switch `{:s}` to monitor mode'.format(ifname))
		return False
	print('Switched `{:s}` to monitor mode'.format(ifname))

	turn_on_iface(ifname)

	# change channel
	if channel is not None:
		cmd_channel = 'sudo iwconfig {:s} channel {:d}'.format(ifname, channel)
		shell_output = run_shell(cmd_channel)
		stderr_str = str(shell_output.stderr).strip()
		if len(stderr_str) > 0:
			print('Could not switch `{:s}` to channel {:d}'.format(ifname, channel))
			return False
		print('Switched `{:s}` to channel {:d}'.format(ifname, channel))

	return True
