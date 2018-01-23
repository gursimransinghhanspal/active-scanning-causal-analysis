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
command = 'tshark -E separator=, -T fields -e frame.number -e frame.time_epoch -e frame.len -e radiotap.channel.freq ' \
          '-e radiotap.mactime -e radiotap.datarate -e wlan.fc.type_subtype -e wlan.bssid ' \
          '-e wlan.fc.retry -e wlan.fc.pwrmgt ' \
          '-e wlan.fc.moredata -e wlan.fc.frag -e wlan.duration -e wlan.ra -e wlan.ta -e wlan.sa -e wlan.da ' \
          '-e wlan.seq -e wlan.qos.priority -e wlan.qos.amsdupresent -e wlan.fc.type ' \
          '-e wlan.fc.ds -e radiotap.dbm_antsignal -r ' + '\'{0}\' ' + '>> \'{1}\''

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

		hardname = 'DFL_Exp' + str(idx + 1) + '-c0_ee_fb_30_d7_17.csv'
		csvfile = os.path.join(RAW_CSV_DIR, hardname)

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
