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
	# this also turns the iface on (obviously)
	iface_sniff(ifname, channel)
	# start the capture
	print("start_capture(): starting capture - `{:s}`. [{:f}]".format(start_capture_command, time()))
	out = execute_in_shell(start_capture_command, stdout = subprocess.DEVNULL)
	print("start_capture(): rc = {:d}. [{:f}]".format(out.returncode, time()))
	return out.returncode


def stop_all_captures():
	"""
	Kills all tshark processes
	:return:
	"""

	stop_capture_command = 'sudo killall tshark'
	print("stop_all_captures(): killing all tshark processes - `{:s}`. [{:f}]".format(stop_capture_command,
		                                                                                  time()))
	output = execute_in_shell(stop_capture_command)
	if output.returncode == 0:
		print('stop_all_captures(): capture completed! [{:f}]'.format(time()))
	return output.returncode


if __name__ == "__main__":
	pass
