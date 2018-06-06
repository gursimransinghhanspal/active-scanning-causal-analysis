"""
Helper script with methods regarding command execution on terminal/shell

NOTE:
	- all commands run on the default shell
	- most commands in the script are meant for `bourne shell`
"""

import subprocess
from typing import Union


def whatis_default_shell():
	pass


def execute_in_shell(command: Union[str, list], stdout = subprocess.PIPE, stderr = subprocess.STDOUT):
	"""
	Execute the command in the default shell
	"""

	return subprocess.run(
		args = command,
		shell = True,
		stdout = stdout,
		stderr = stderr,
		universal_newlines = True
	)
	pass
