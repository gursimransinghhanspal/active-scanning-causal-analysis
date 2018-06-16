"""

"""

import os
from shutil import rmtree
from time import time


def initialize_directory_counter(root_save_dir) -> int:
	"""
	Looks through the directory for the next counter value to continue the session
	"""

	ls = os.listdir(root_save_dir)
	if len(ls) == 0:
		return 1

	# noinspection PyBroadException
	try:
		ls = [int(i) for i in ls]
	except:
		print("initialize_directory_counter(): initializing the `dir-counter` to default value. [{:f}]".format(time()))
		return 1

	ls.sort()
	value = ls[-1] + 1
	print("initialize_directory_counter(): initializing the `dir-counter` to {:d}. [{:f}]".format(value, time()))
	return value


def delete_directory(dir_path):
	print("delete_directory(): deleting... {:s}. [{:f}]".format(str(dir_path), time()))
	rmtree(dir_path)


if __name__ == "__main__":
	pass
