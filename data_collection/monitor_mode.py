from data_collection.aux import run_shell


def switch_to_monitor_mode(ifname, channel: int = None):
	"""

	:param ifname:
	:param channel:
	:return:
	"""

	cmd_down = 'sudo ifconfig {:s} down'.format(ifname)
	cmd_monitor = 'sudo iwconfig {:s} mode monitor'.format(ifname)
	cmd_up = 'sudo ifconfig {:s} up'.format(ifname)

	# turn off the device
	run_shell(cmd_down)

	# switch to monitor mode
	run_shell(cmd_monitor)

	# turn on the device
	run_shell(cmd_up)

	# change channel
	if channel is not None:
		cmd_channel = 'sudo iwconfig {:s} channel {:d}'.format(ifname, channel)
		run_shell(cmd_channel)
