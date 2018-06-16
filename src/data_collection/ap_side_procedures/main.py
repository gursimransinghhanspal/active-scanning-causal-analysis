from time import sleep, time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from data_collection.ap_side_procedures.env import *
from data_collection.util.directory_utility import delete_directory, initialize_directory_counter
from data_collection.util.iface_utility import does_iface_exist, iface_dn
from data_collection.util.tshark_utility import start_capture, stop_all_captures
from data_collection.util.wpa_utility import associate_sta, disassociate_all_sta

#
# ***** constants related to TP-LINK AC1300 router *****
#
# Login
_ELEMENT_ID__INPUT__USERNAME = "userName"
_ELEMENT_ID__INPUT__PASSWORD = "pcPassword"
_ELEMENT_ID__BUTTON__LOGIN = "loginBtn"
# Main
_ELEMENT_ID__ANCHOR__BASIC = "basic"
_ELEMENT_ID__CONTROL__LOGOUT = "top-control-logout"
# Basic
_ELEMENT_ID__LIST_ITEM__WIRELESS = "wireless_menu"
# Wireless Menu
_ELEMENT_ID__FORM__WIRELESS = "form-wireless"
_ELEMENT_ID__INPUT__PASSWORD_2G = "password_2G"
_ELEMENT_ID__BUTTON__SAVE = "btn-save"

# the directory name counter
# no need to change, gets initialized automatically
_DIR_NAME_COUNTER = 1


#
# ***** begin ***** #
#

def _prepare_environment() -> int:
	"""
	Does initial checks and some mundane setup to begin
	:return: the initial dir name counter value
	"""

	ok = True

	# *** do all interfaces exist ***
	all_ifaces = [iface for _, iface in SNIFFER_INTERFACES]
	all_ifaces.extend(CLIENT_INTERFACES)

	print("Checking all interfaces:")
	for ifname in all_ifaces:
		if not does_iface_exist(ifname):
			print("• `{:s}` does not exist!".format(ifname))
			ok = False
		else:
			print("• `{:s}` exists!".format(ifname))
	print()

	# *** reset ***
	_reset(None)

	# *** create root_save_dir if does not exist ***
	os.makedirs(ROOT_SAVE_DIR_PATH, exist_ok = True)
	print()
	print()

	# *** status ***
	return ok


def _reset(save_dir_path):
	"""
	Resets the environment

	:param save_dir_path: if provided, deletes the directory... should be used when some error occurs
	:return:
	"""

	print("+" * 40)
	print("Resetting environment")
	print()

	if save_dir_path is not None:
		delete_directory(save_dir_path)

	# stop current ongoing capture
	stop_all_captures()
	# disassociate all clients
	disassociate_all_sta(CLIENT_INTERFACES)

	# turn off all interfaces
	# sniffers
	for _, ifname in SNIFFER_INTERFACES:
		iface_dn(ifname = ifname)
	# clients
	for ifname in CLIENT_INTERFACES:
		iface_dn(ifname = ifname)

	print()
	print("+" * 40)
	print()


def _change_router_password(password: str) -> int:
	"""
	Change the wireless password for the router using Selenium
	"""

	# Get the web driver
	driver = webdriver.Chrome()
	# Request the URL and wait for it to load
	driver.get(ROUTER_ADMIN_SITE_URL)

	# Login
	input__admin_username = driver.find_element_by_id(_ELEMENT_ID__INPUT__USERNAME)
	input__admin_username.send_keys(ROUTER_ADMIN_USERNAME)
	input__admin_password = driver.find_element_by_id(_ELEMENT_ID__INPUT__PASSWORD)
	input__admin_password.send_keys(ROUTER_ADMIN_PASSWORD)
	button__login = driver.find_element_by_id(_ELEMENT_ID__BUTTON__LOGIN)
	button__login.click()

	# Click on `Basic` tab
	# wait for basic anchor to be present
	try:
		anchor__basic = WebDriverWait(driver = driver, timeout = 10).until(
			expected_conditions.presence_of_element_located((By.ID, _ELEMENT_ID__ANCHOR__BASIC))
		)
	except TimeoutException:
		print("_toggle_router_password(): could not find the `Basic` tab.")
		return 1
	else:
		# click the basic anchor
		anchor__basic.click()

	# Click on `Wireless` menu item
	# wait for the wireless menu to be present
	try:
		list_item__wireless = WebDriverWait(driver = driver, timeout = 10).until(
			expected_conditions.presence_of_element_located((By.ID, _ELEMENT_ID__LIST_ITEM__WIRELESS))
		)
	except TimeoutException:
		print("_toggle_router_password(): could not find the `Wireless` menu item.")
		return 2
	else:
		# click the wireless menu
		list_item__wireless.click()

	# Switch to the child <iframe>
	iframe__wireless = driver.find_element_by_id("frame")
	driver.switch_to.frame(iframe__wireless)

	# Fill in the new password and save
	# wait for wireless form to be present
	try:
		WebDriverWait(driver = driver, timeout = 10).until(
			expected_conditions.presence_of_element_located((By.ID, _ELEMENT_ID__FORM__WIRELESS))
		)
	except TimeoutException:
		print("_toggle_router_password(): could not find the `Wireless` form.")
		return 3
	else:
		# fill in the new password
		input__password_2g = driver.find_element_by_name(_ELEMENT_ID__INPUT__PASSWORD_2G)
		input__password_2g.clear()
		input__password_2g.send_keys(password)

		# click the save button
		button__save = driver.find_element_by_id(_ELEMENT_ID__BUTTON__SAVE)
		button__save.click()

	# Switch to the parent <iframe>
	driver.switch_to.parent_frame()

	# Logout
	# wait for wireless form to reload (to know that saving is complete)
	try:
		WebDriverWait(driver = driver, timeout = 10).until(
			expected_conditions.presence_of_element_located((By.ID, _ELEMENT_ID__CONTROL__LOGOUT))
		)
	except TimeoutException:
		print("_toggle_router_password(): could not find the `Wireless` form after saving.")
		return 4
	else:
		anchor__logout = driver.find_element_by_id(_ELEMENT_ID__CONTROL__LOGOUT)
		anchor__logout.click()

	driver.close()
	driver.quit()
	return 0


def _collect():
	"""
	Collects one episode per client
	"""

	global _DIR_NAME_COUNTER

	print("-" * 40)
	print("-" * 40)
	print("_collect(): Starting collection {:d}. [{:f}]".format(_DIR_NAME_COUNTER, time()))

	_save_dir_path = os.path.join(ROOT_SAVE_DIR_PATH, str(_DIR_NAME_COUNTER))
	if os.path.exists(_save_dir_path):
		print("_collect(): Something has gone wrong! directory `{:s}` already exists".format(str(_save_dir_path)))
		return False
	else:
		os.mkdir(_save_dir_path)

	# *** actual work starts here ***

	# change password to the conf password
	rc = _change_router_password(password = ROUTER_WIRELESS_CONF_PASSWORD)
	if rc != 0:
		_reset(_save_dir_path)
	print("." * 40)
	print()

	# give some time to settle in
	sleep(30)

	# associate clients
	# - associate each client to the ap with a sleep time of 10s in between
	#   - gives ample time to complete the handshake
	#   - reduces frame collision between multiple clients
	for ifname in CLIENT_INTERFACES:
		_ok = associate_sta(ifname, WPA_SUPPLICANT_CONF_PATH, assert_association = True)
		sleep(10)
		if not _ok:
			_reset(_save_dir_path)
			return
	print("." * 40)
	print()

	# start sniffing
	for channel, ifname in SNIFFER_INTERFACES:
		rc = start_capture(ifname, channel, _DIR_NAME_COUNTER, _save_dir_path)
		if rc != 0:
			_reset(_save_dir_path)
			return
	print("." * 40)
	print()

	# buffer time to populate pcapng file
	sleep(60)

	# change the router password to the alternate password
	rc = _change_router_password(password = ROUTER_WIRELESS_ALT_PASSWORD)
	if rc != 0:
		_reset(_save_dir_path)
		return
	print("." * 40)
	print()

	# buffer time to populate pcapng file
	sleep(60)

	# stop current ongoing capture
	stop_all_captures()
	# disassociate all clients
	disassociate_all_sta(CLIENT_INTERFACES)

	# turn off all interfaces
	# sniffers
	for _, ifname in SNIFFER_INTERFACES:
		iface_dn(ifname = ifname)
	# clients
	for ifname in CLIENT_INTERFACES:
		iface_dn(ifname = ifname)

	# update counter
	_DIR_NAME_COUNTER += 1

	print()
	print("_collect(): Completed collection of one episode per client. [{:f}]".format(time()))
	print("-" * 40)
	print("-" * 40)
	print()
	return True


def main():
	ok = _prepare_environment()

	# initialize the dir name counter
	global _DIR_NAME_COUNTER
	_DIR_NAME_COUNTER = initialize_directory_counter(ROOT_SAVE_DIR_PATH)

	while ok:
		ok = _collect()
		# buffer time between collections
		sleep(10)

		# always collect
		# comment the following statement to stop the script when a collection attempt fails
		ok = True


if __name__ == '__main__':
	main()
