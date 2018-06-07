"""

"""

import os
from shutil import rmtree


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
		return 1

	ls.sort()
	return ls[-1] + 1


def delete_directory(dir_path):
	rmtree(dir_path)


if __name__ == "__main__":
	pass
