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
AP_IP_ADDRESS = "10.0.0.1"
AP_NETMASK = "24"
AP_CHANNEL = 6

# a list of all clients
CLIENT_INTERFACES = [
	"",
	"",
]

# path to root directory where to save capture files
ROOT_SAVE_DIR_PATH = os.path.abspath("")

# path to wpa_supplicant conf file
WPA_SUPPLICANT_CONF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wpa_supplicant.conf")
# path to hostapd executable
HOSTAPD_EXEC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hostapd-2.6/hostapd/hostapd")
# path to hostapd conf file
HOSTAPD_CONF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hostapd-2.6/hostapd/hostapd.conf")

if __name__ == '__main__':
	print("SNIFFER_INTERFACES:")
	print(str(SNIFFER_INTERFACES))
	print()

	print("AP_INTERFACE: " + str(AP_INTERFACE))
	print("AP_IP_ADDRESS: " + str(AP_IP_ADDRESS))
	print("AP_NETMASK: " + str(AP_NETMASK))
	print("AP_CHANNEL: " + str(AP_CHANNEL))
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
