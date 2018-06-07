import os
import subprocess
from time import time

from data_collection.aux.iface_utility import iface_sniff
from data_collection.aux.shell_utility import execute_in_shell


def start_capture(ifname, channel, dir_name_counter, save_dir_name):
	"""
	Start a frame capture on the give interface using tshark
	:return:
	"""

	# filename
	filename_fmt = 'control_ce_{:05d}_ch{:02d}.pcapng'
	filename = filename_fmt.format(dir_name_counter, channel)
	file = os.path.abspath(os.path.join(save_dir_name, filename))
	# capture command
	start_capture_command_fmt = 'sudo tshark -i {:s} -w {:s} &'
	start_capture_command = start_capture_command_fmt.format(ifname, str(file))

	# put interface in monitor mode, and sniff on the channel
	iface_sniff(ifname, channel)
	# start the capture
	execute_in_shell(start_capture_command, stdout = subprocess.DEVNULL)
	print('capture started on channel `{:d}` using iface `{:s}`, epoch: {:f}'.format(channel, ifname, time()))


def stop_all_captures():
	"""
	Kills all tshark processes
	:return:
	"""

	stop_capture_command = 'sudo killall tshark'
	while True:
		output = execute_in_shell(stop_capture_command)
		# ideally should stop in first try
		if output.returncode == 0:
			print('capture completed!, epoch: {:f}'.format(time()))
			break


if __name__ == "__main__":
	pass
