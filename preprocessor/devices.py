"""
This file is used to define all the arguments (till the command parser is ready)
	- Client Mac Addresses to process
	- Access Point Mac Addresses to process
"""

import os

from dotenvy import read_file

env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
env_config = read_file(env_file)

# client devices mac addresses
gursimran_iphone_6s = str(env_config['GURSIMRAN_IPHONE_6S']).strip().lower()
gursimran_oneplus_one = str(env_config['GURSIMRAN_ONEPLUS_ONE']).strip().lower()
gursimran_macbook_pro = str(env_config['GURSIMRAN_MACBOOK_PRO']).strip().lower()
gursimran_desktop_linux = str(env_config['GURSIMRAN_DESKTOP']).strip().lower()
harish_moto_g4 = str(env_config['HARISH_MOTO_G4']).strip().lower()
dheryta_nexus_4 = str(env_config['DHERYTA_NEXUS_4']).strip().lower()
dheryta_sony_xperia = str(env_config['DHERYTA_SONY_XPERIA']).strip().lower()
dheryta_samsung_gt_s5560v = str(env_config['DHERYTA_SAMSUNG_GT_S5560V']).strip().lower()
dheryta_samsung_sgh_i917 = str(env_config['DHERYTA_SAMSUNG_SGH_i917']).strip().lower()
dheryta_samsung_gt_s6802 = str(env_config['DHERYTA_SAMSUNG_GT_S6802']).strip().lower()
dheryta_ipad = str(env_config['DHERYTA_IPAD']).strip().lower()

# access points
gursimran_netgear_1 = str(env_config['GURSIMRAN_NETGEAR_1']).strip().lower()
gursimran_netgear_2 = str(env_config['GURSIMRAN_NETGEAR_2']).strip().lower()
dheryta_netgear = str(env_config['DHERYTA_NETGEAR']).strip().lower()
dheryta_tplink = str(env_config['DHERYTA_TPLINK']).strip().lower()

if __name__ == '__main__':
	print(gursimran_iphone_6s)
	print(gursimran_oneplus_one)
	print(gursimran_macbook_pro)
	print(gursimran_desktop_linux)
	print(harish_moto_g4)
	print(dheryta_nexus_4)
	print(dheryta_sony_xperia)
	print(dheryta_samsung_gt_s5560v)
	print(dheryta_samsung_sgh_i917)
	print(dheryta_samsung_gt_s6802)
	print(dheryta_ipad)
	print(gursimran_netgear_1)
	print(gursimran_netgear_2)
	print(dheryta_netgear)
	print(dheryta_tplink)
