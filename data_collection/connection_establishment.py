"""
A simple script to collect data for the cause `connection establishment`

Steps:
	- start capture -- on channel 1, 6 and 11
	- wait 30 seconds
	- connect all specified clients to the access point
	- make sure all clients have connected properly,
		- if not, delete this capture session (fail-safe)
	- wait 30 seconds
	- stop the capture
	- disconnect all the clients

	- - - rinse and repeat - - -
"""

import os
import subprocess

# #############################################################################
# ### Constants ###
# #############################################################################

# wpa_supplicant.conf file
#   - should have the `ssid`, `passphrase` generated using wpa_passphrase command
#   - also include the `bssid`
# sample file:

__WPA_CONF = os.path.abspath(__file__)

# list of client device interfaces
__CLIENTS = [
	'wlps10',

]


def check_client_iface_exists():
	"""
	A simple call to `iwconfig <iface>` tells if the client is connected or not
	"""

	connected = True
	command_fmt = 'iwconfig {:s}'

	for iface in __CLIENTS:
		command = command_fmt.format(iface)
		shell_output = subprocess.run(
			command,
			shell = True,
			stdout = subprocess.PIPE,
			universal_newlines = True
		)
		shell_output = str.strip(shell_output)

		if len(shell_output) == 0:
			connected = False
			print('{:s} not connected to the machine. Please check all devices are connected!'.format(iface))
		else:
			print('{:s} connected.'.format(iface))
	return connected


check_client_iface_exists()
