import subprocess


def run_shell(command: str, output = subprocess.PIPE):
	"""
	Runs a command using the default shell
	:return:
	"""

	return subprocess.run(
		command,
		shell = True,
		stdout = output,
		stderr = output,
		universal_newlines = True
	)
