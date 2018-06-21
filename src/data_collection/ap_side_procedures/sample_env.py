import os

"""
The sample configuration file for ap side procedures cause data collection
	- Copy/Rename this file into 'env.py'
	- Define all the environment variables in 'env.py' before running the collection script
	- DO NOT commit 'env.py' to source control
"""

SNIFFER_INTERFACES = [
	(1, ""),
	(6, ""),
	(11, ""),
]

# a list of all clients
CLIENT_INTERFACES = [
	"",
	"",
]

# router properties
ROUTER_ADMIN_SITE_URL = "http://192.168.0.1"
ROUTER_ADMIN_USERNAME = "admin"
ROUTER_ADMIN_PASSWORD = "admin"

ROUTER_WIRELESS_CONF_PASSWORD = "1234567890abc"
ROUTER_WIRELESS_ALT_PASSWORD = "0987654321"

# path to root directory where to save capture files
ROOT_SAVE_DIR_PATH = os.path.abspath("")

# path to wpa_supplicant conf file
WPA_SUPPLICANT_CONF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wpa_supplicant.conf")

if __name__ == '__main__':
	print("SNIFFER_INTERFACES:")
	print(str(SNIFFER_INTERFACES))
	print()

	print("ROUTER_ADMIN_SITE_URL: " + str(ROUTER_ADMIN_SITE_URL))
	print("ROUTER_ADMIN_USERNAME: " + str(ROUTER_ADMIN_USERNAME))
	print("ROUTER_ADMIN_PASSWORD: " + str(ROUTER_ADMIN_PASSWORD))
	print("ROUTER_WIRELESS_CONF_PASSWORD: " + str(ROUTER_WIRELESS_CONF_PASSWORD))
	print("ROUTER_WIRELESS_ALT_PASSWORD: " + str(ROUTER_WIRELESS_ALT_PASSWORD))
	print()

	print("CLIENT_INTERFACES:")
	print(str(CLIENT_INTERFACES))
	print()

	print("ROOT_SAVE_DIR_PATH: " + str(ROOT_SAVE_DIR_PATH))
	print("WPA_SUPPLICANT_CONF_PATH: " + str(WPA_SUPPLICANT_CONF_PATH))
	print()
	pass
