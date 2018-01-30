import os
import subprocess

# get current directory
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
# pcaps directory
PCAPS_DIR = os.path.join(PROJECT_DIR, 'pcap')
# csv directory
RAW_CSV_DIR = os.path.join(PROJECT_DIR, 'raw_csv')

# Supported Extensions
SUPPORTED_EXTS = ['.pcap', ]

# create directories if don't exist
if not os.path.exists(PCAPS_DIR) or not os.path.isdir(PCAPS_DIR):
	os.mkdir(PCAPS_DIR)
if not os.path.exists(RAW_CSV_DIR) or not os.path.isdir(RAW_CSV_DIR):
	os.mkdir(RAW_CSV_DIR)

# make sure CSV_DIR is empty
if len(os.listdir(RAW_CSV_DIR)) != 0:
	print(RAW_CSV_DIR, 'is not empty! Please empty the directory and try again.')
	exit(0)

# use t-shark
#   - create csv from pcaps with the same name
space = ' '
command = 'tshark -E separator=, -T fields' + space + \
          '-e frame.number' + space + \
          '-e frame.time_epoch' + space + \
          '-e frame.len' + space + \
          '-e radiotap.channel.freq' + space + \
          '-e radiotap.mactime' + space + \
          '-e radiotap.datarate' + space + \
          '-e wlan.fc.type_subtype' + space + \
          '-e wlan_mgt.ssid' + space + \
          '-e wlan.bssid' + space + \
          '-e wlan_mgt.ds.current_channel' + space + \
          '-e wlan_mgt.qbss.scount' + space + \
          '-e wlan.fc.retry' + space + \
          '-e wlan.fc.pwrmgt' + space + \
          '-e wlan.fc.moredata' + space + \
          '-e wlan.fc.frag' + space + \
          '-e wlan.duration' + space + \
          '-e wlan.ra' + space + \
          '-e wlan.ta' + space + \
          '-e wlan.sa' + space + \
          '-e wlan.da' + space + \
          '-e wlan.seq' + space + \
          '-e wlan.qos.priority' + space + \
          '-e wlan.qos.amsdupresent' + space + \
          '-e wlan.fc.type' + space + \
          '-e wlan_mgt.fixed.reason_code' + space + \
          '-e wlan_mgt.fixed.status_code' + space + \
          '-e wlan.fc.ds' + space + \
          '-e radiotap.dbm_antsignal' + space + \
          '-r ' + '\'{0}\' ' + '>> \'{1}\''

# create csv header
args = command.split(' ')
csv_header = list()
for i in range(1, len(args)):
	if args[i - 1] == '-e':
		csv_header.append(args[i])
csv_header.append('radiotap.dbm_antsignal2')

csv_header_string = str.join(',', csv_header)
csv_header_string += '\n'


def main():
	# read all pcap file-names
	pcap_files = list()
	for file in os.listdir(PCAPS_DIR):
		if os.path.splitext(file)[1] in SUPPORTED_EXTS:
			pcap_files.append(file)

	# create csv from pcaps
	pcap_files.sort()
	for idx, pcapname in enumerate(pcap_files):
		basename = os.path.splitext(pcapname)[0]
		csvname = basename + '.csv'
		pcapfile = os.path.join(PCAPS_DIR, pcapname)
		csvfile = os.path.join(RAW_CSV_DIR, csvname)

		# create file and add header on top
		with open(csvfile, 'w') as file:
			file.write(csv_header_string)
			file.close()

		# append data
		cmd = command.format(str(pcapfile), str(csvfile))
		p = subprocess.Popen(cmd, shell = True)
		os.waitpid(p.pid, 0)


if __name__ == "__main__":
	main()
