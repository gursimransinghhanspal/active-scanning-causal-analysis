from selenium import webdriver
from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

_ADMIN_USERNAME = "admin"
_ADMIN_PASSWORD = "admin"

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


def _change_password(new_pass: str):
	driver = webdriver.Chrome()
	driver.get("http://192.168.0.1")

	# Login
	input__username = driver.find_element_by_id(_ELEMENT_ID__INPUT__USERNAME)
	input__username.send_keys(_ADMIN_USERNAME)
	input__password = driver.find_element_by_id(_ELEMENT_ID__INPUT__PASSWORD)
	input__password.send_keys(_ADMIN_PASSWORD)
	button__login = driver.find_element_by_id(_ELEMENT_ID__BUTTON__LOGIN)
	button__login.click()

	# Click on `Basic` tab
	# wait for basic anchor to be present
	try:
		anchor__basic = WebDriverWait(driver = driver, timeout = 10).until(
			expected_conditions.presence_of_element_located((By.ID, _ELEMENT_ID__ANCHOR__BASIC))
		)
	except TimeoutException:
		print("A")
		exit(1)
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
		print("B")
		exit(1)
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
		print("C")
		exit(1)
	else:
		# fill in the new password
		input__password_2g = driver.find_element_by_name(_ELEMENT_ID__INPUT__PASSWORD_2G)
		input__password_2g.clear()
		input__password_2g.send_keys(new_pass)

		# click the save button
		button__save = driver.find_element_by_id(_ELEMENT_ID__BUTTON__SAVE)
		button__save.click()

	# Switch to the parent <iframe>
	driver.switch_to.parent_frame()

	# Logout
	# wait for wireless form to reload
	try:
		WebDriverWait(driver = driver, timeout = 10).until(
			expected_conditions.presence_of_element_located((By.ID, _ELEMENT_ID__CONTROL__LOGOUT))
		)
	except TimeoutException:
		print("D")
		exit(1)
	else:
		anchor__logout = driver.find_element_by_id(_ELEMENT_ID__CONTROL__LOGOUT)
		anchor__logout.click()

	driver.close()
	driver.quit()


if __name__ == '__main__':
	_change_password("0987654321")
