import os

"""
The configuration file for beacon loss cause data collection
"""

SNIFFER_INTERFACES = [
	(1, ""),
	(6, ""),
	(11, ""),
]

# access point interface
AP_INTERFACE = ""

# a list of all clients
CLIENT_INTERFACES = [
	"",
	"",
]

# path to root directory where to save capture files
ROOT_SAVE_DIR_PATH = os.path.abspath('')

# path to wpa_supplicant conf file
WPA_SUPPLICANT_CONF_PATH = os.path.abspath('')
# path to hostapd executable
HOSTAPD_EXEC_PATH = os.path.abspath('')
# path to hostapd conf file
HOSTAPD_CONF_PATH = os.path.abspath('')

if __name__ == '__main__':
	print("SNIFFER_INTERFACES:")
	print(str(SNIFFER_INTERFACES))
	print()

	print("AP_INTERFACE: " + str(AP_INTERFACE))
	print()

	print("CLIENT_INTERFACES:")
	print(str(CLIENT_INTERFACES))
	print()

	print("ROOT_SAVE_DIR_PATH: " + str(ROOT_SAVE_DIR_PATH))
	print("WPA_SUPPLICANT_CONF_PATH: " + str(WPA_SUPPLICANT_CONF_PATH))
	print("HOSTAPD_EXEC_PATH: " + str(HOSTAPD_EXEC_PATH))
	print("HOSTAPD_CONF_PATH: " + str(HOSTAPD_CONF_PATH))
	print()
	pass
