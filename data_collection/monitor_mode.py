from data_collection.aux import run_shell


def turn_off_iface(ifname):
	"""

	:param ifname:
	:return:
	"""

	cmd_down = 'sudo ifconfig {:s} down'.format(ifname)
	run_shell(cmd_down)


def turn_on_iface(ifname):
	"""

	:param ifname:
	:return:
	"""

	cmd_up = 'sudo ifconfig {:s} up'.format(ifname)
	run_shell(cmd_up)


def switch_to_monitor_mode(ifname, channel: int = None):
	"""

	:param ifname:
	:param channel:
	:return:
	"""

	cmd_monitor = 'sudo iwconfig {:s} mode monitor'.format(ifname)

	turn_off_iface(ifname)
	run_shell(cmd_monitor)
	turn_on_iface(ifname)

	# change channel
	if channel is not None:
		cmd_channel = 'sudo iwconfig {:s} channel {:d}'.format(ifname, channel)
		run_shell(cmd_channel)
