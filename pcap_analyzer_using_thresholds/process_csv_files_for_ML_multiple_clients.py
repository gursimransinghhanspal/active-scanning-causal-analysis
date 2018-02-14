import os
import threading

import pandas as pd


def get_tag_for_cause(cause):
	string = 'X'
	if cause == 'cause.unsuccessAssoc':
		string = 'a'
	elif cause == 'cause.class3':
		string = 'b'
	elif cause == 'cause.successAssoc':
		string = 'c'
	elif cause == 'cause.lowrssi':
		string = 'd'
	elif cause == 'cause.powerstate':
		string = 'e'
	elif cause == 'cause.powerstateV2':
		string = 'f'
	if cause == 'cause.apsideproc':
		string = 'g'
	elif cause == 'cause.beaconloss':
		string = 'h'
	elif cause == 'cause.dataframeloss':
		string = 'i'
	elif cause == 'cause.clientdeauth':
		string = 'm'
	return string


def merge_dictionaries(*dict_args):
	result = {}
	for dictionary in dict_args:
		result.update(dictionary)
	return result


def rbs__low_rssi(dataframe, episode_min_idx, episode_max_idx, clients: list):
	"""
	For every episode, calculate `mean` and `standard deviation` for rssi value.
	check: `mean` < -72dB and `std dev` > 12dB
	"""

	output_dict = {
		'ssi.mean': [],
		'ssi.sd': [],
		'cause.lowrssi': [],
		'start.time': [],
		'end.time': [],
		'duration.time': []
	}

	for episode_idx in range(episode_min_idx, episode_max_idx + 1):
		# filter:
		#   - episode index = `episode_idx`
		_df_episode = dataframe[
			(dataframe['episode'] == episode_idx)
		]

		# filter:
		#   - episode index = `episode_idx`
		#   - either source address or transmitter address should be in `clients`
		_df_client_episode = _df_episode[
			(_df_episode['wlan.sa'].isin(clients) | _df_episode['wlan.ta'].isin(clients))
		]

		# calculate `mean` and `std dev`
		rssi_mean = _df_client_episode['radiotap.dbm_antsignal'].mean()
		rssi_stddev = _df_client_episode['radiotap.dbm_antsignal'].std()

		# check metric
		cause = str(False)
		if rssi_mean < -72 and rssi_stddev > 12:
			cause = str(True)

		# append data to output dictionary
		start_epoch = float((_df_episode.head(1))['frame.time_epoch'])
		end_epoch = float((_df_episode.tail(1))['frame.time_epoch'])

		output_dict['ssi.mean'].append(rssi_mean)
		output_dict['ssi.sd'].append(rssi_stddev)
		output_dict['cause.lowrssi'].append(cause)
		output_dict['start.time'].append(start_epoch)
		output_dict['end.time'].append(end_epoch)
		output_dict['duration.time'].append(float((end_epoch - start_epoch) / 60))
	return output_dict


def rbs__data_frame_loss(dataframe, episode_min_idx, episode_max_idx, clients: list):
	"""
	use `fc.retry` field
	check: #(fc.retry == 1)/#(fc.retry == 1 || fc.retry == 0) > 0.5
	"""

	output_dict = {
		'frame.lossrate': [],
		'cause.dataframeloss': []
	}

	for episode_idx in range(episode_min_idx, episode_max_idx + 1):
		# filter:
		#   - episode index = `episode_idx`
		_df_episode = dataframe[
			(dataframe['episode'] == episode_idx)
		]

		# filter:
		#   - episode index = `episode_idx`
		#   - `fc.retry` == 1
		#   - either source address or transmitter address should be in `clients`
		_df_retry_true = _df_episode[
			((_df_episode['wlan.fc.retry'] == 1) &
			 (_df_episode['wlan.sa'].isin(clients) | _df_episode['wlan.ta'].isin(clients)))
		]

		# filter:
		#   - episode index = `episode_idx`
		#   - `fc.retry` == 0
		#   - either source address or transmitter address should be in `clients`
		_df_retry_false = _df_episode[
			((_df_episode['wlan.fc.retry'] == 0) &
			 (_df_episode['wlan.sa'].isin(clients) | _df_episode['wlan.ta'].isin(clients)))
		]

		# calculate ratios and check
		num_true = len(_df_retry_true)
		num_false = len(_df_retry_false)

		if num_true + num_false > 0:
			ratio = float(num_true) / float(num_true + num_false)
		else:
			ratio = -1  # could not calculate

		# check metric
		cause = str(False)
		if ratio > 0.5:
			cause = str(True)

		# append data to output dictionary
		output_dict['frame.lossrate'].append(ratio)
		output_dict['cause.dataframeloss'].append(cause)

	return output_dict


def rbs__power_state_low_to_high_v1(dataframe, episode_min_idx, episode_max_idx, clients: list):
	"""
	calculate number of frames per second.
	check: if #fps > 2
	"""

	output_dict = {
		'frames.persec': [],
		'cause.powerstate': []
	}

	for episode_idx in range(episode_min_idx, episode_max_idx + 1):
		# filter:
		#   - episode index = `episode_idx`
		#   - either source address or transmitter address should be in `clients`
		_df_client_episode = dataframe[
			((dataframe['episode'] == episode_idx) &
			 (dataframe['wlan.sa'].isin(clients) | dataframe['wlan.ta'].isin(clients)))
		]

		# append data to output dictionary, if no frames found
		if len(_df_client_episode) == 0:
			output_dict['frames.persec'].append(0)
			output_dict['cause.powerstate'].append(str(False))
			continue

		# calculate metrics
		start_epoch = float(_df_client_episode.head(1)['frame.time_epoch'])
		end_epoch = float(_df_client_episode.tail(1)['frame.time_epoch'])
		window_duration = end_epoch - start_epoch
		num_of_frames = len(_df_client_episode)

		metric = -1
		if num_of_frames > 1 and window_duration > 0:
			metric = float(num_of_frames) / float(window_duration)

		# check metric
		cause = str(False)
		if metric == -1:
			cause = 'Invalid'
		elif metric > 2:
			cause = str(True)

		# append data to output dictionary
		output_dict['frames.persec'].append(metric)
		output_dict['cause.powerstate'].append(cause)
	return output_dict


def rbs__power_state_low_to_high_v2(dataframe, episode_min_idx, episode_max_idx, clients: list):
	"""
	calculate number of frames per second.
	check: if #fps <= 2
	"""

	output_dict = {
		'cause.powerstateV2': []
	}

	for episode_idx in range(episode_min_idx, episode_max_idx + 1):
		# filter:
		#   - episode index = `episode_idx`
		#   - either source address or transmitter address should be in `clients`
		_df_client_episode = dataframe[
			((dataframe['episode'] == episode_idx) &
			 (dataframe['wlan.sa'].isin(clients) | dataframe['wlan.ta'].isin(clients)))
		]

		# append data to output dictionary, if no frames found
		if len(_df_client_episode) == 0:
			output_dict['cause.powerstateV2'].append(str(True))
			continue

		# calculate metrics
		start_epoch = float(_df_client_episode.head(1)['frame.time_epoch'])
		end_epoch = float(_df_client_episode.tail(1)['frame.time_epoch'])
		window_duration = end_epoch - start_epoch
		num_of_frames = len(_df_client_episode)

		metric = -1
		if num_of_frames > 1 and window_duration > 0:
			metric = float(num_of_frames) / float(window_duration)

		# check metric
		cause = str(False)
		if metric == -1:
			cause = 'Invalid'
		elif metric <= 2:
			cause = str(True)

		# append data to output dictionary
		output_dict['cause.powerstateV2'].append(cause)
	return output_dict


def rbs__ap_deauth(dataframe, episode_min_idx, episode_max_idx, clients: list):
	"""
	check for deauth packet from ap
	deauth: fc.type_subtype == 12
	"""

	output_dict = {
		'ap.deauth.count': [],
		'cause.apsideproc': []
	}

	for episode_idx in range(episode_min_idx, episode_max_idx + 1):
		# filter:
		#   - episode index = `episode_idx`
		#   - packet type = `deauth`
		#   - destination address should be in `clients`
		_df_episode = dataframe[
			((dataframe['episode'] == episode_idx) &
			 (dataframe['wlan.fc.type_subtype'] == 12) &
			 (dataframe['wlan.da'].isin(clients)))
		]

		# calculate metrics
		metric = len(_df_episode)

		# check metric
		cause = str(False)
		if metric > 0:
			cause = str(True)

		# append data to output dictionary
		output_dict['ap.deauth.count'].append(metric)
		output_dict['cause.apsideproc'].append(cause)
	return output_dict


def rbs__client_deauth(dataframe, episode_min_idx, episode_max_idx, clients: list):
	"""
	check for deauth packet from client
	deauth: fc.type_subtype == 12
	"""

	output_dict = {
		'client.deauth.count': [],
		'cause.clientdeauth': []
	}

	for episode_idx in range(episode_min_idx, episode_max_idx + 1):
		# filter:
		#   - episode index = `episode_idx`
		#   - packet type = `deauth`
		#   - destination address should be in `clients`
		_df_episode = dataframe[
			((dataframe['episode'] == episode_idx) &
			 (dataframe['wlan.fc.type_subtype'] == 12) &
			 (dataframe['wlan.sa'].isin(clients)))
		]

		# calculate metrics
		metric = len(_df_episode)

		# check metric
		cause = str(False)
		if metric > 0:
			cause = str(True)

		# append data to output dictionary
		output_dict['client.deauth.count'].append(metric)
		output_dict['cause.clientdeauth'].append(cause)
	return output_dict


def rbs__beacon_loss(dataframe, episode_min_idx, episode_max_idx, clients):
	"""
	beacon count is 0 or
	if beacon interval > 105ms for 7 consecutive beacons or
	count(wlan.sa = client and type_subtype = 36|44 and pwrmgt = 0) > 0 and count(wlan.ra = client && type_subtype = 29)
	"""

	output = {
		'beacon.count': [],
		'beacon.interval': [],
		'ack.count': [],
		'ndf.count': [],
		'cause.beaconloss': []
	}

	for episode_idx in range(episode_min_idx, episode_max_idx + 1):
		# filter:
		#   - episode index = `episode_idx`
		#   - packet type = `beacon`
		_df_episode_1 = dataframe[
			((dataframe['episode'] == episode_idx) &
			 (dataframe['wlan.fc.type_subtype'] == 8))
		]

		# calculate metrics
		beacon_count = len(_df_episode_1)

		beacon_interval_count = 0
		if beacon_count > 1:
			previous_epoch = float(_df_episode_1.head(1)['frame.time_epoch'])
			_df_episode_1 = _df_episode_1.iloc[1:]
			for index, frame in _df_episode_1.iterrows():
				current_epoch = float(frame['frame.time_epoch'])
				delta_time = previous_epoch - current_epoch
				if delta_time > 0.105:
					beacon_interval_count += 1
				else:
					beacon_interval_count = 0

				# TODO verify (my addition)
				if beacon_interval_count >= 8:
					break

				previous_epoch = current_epoch

		# filter:
		#   - episode index = `episode_idx`
		#   - packet type = `29`
		#   - receiver address should be in clients
		_df_episode_2 = dataframe[
			((dataframe['episode'] == episode_idx) &
			 (dataframe['wlan.fc.type_subtype'] == 29) &
			 (dataframe['wlan.ra'].isin(clients)))
		]
		ack_count = len(_df_episode_2)

		# filter:
		#   - episode index = `episode_idx`
		#   - packet type = `36` or `44`
		#   - source address should be in clients
		_df_episode_3 = dataframe[
			((dataframe['episode'] == episode_idx) &
			 ((dataframe['wlan.fc.type_subtype'] == 36) | (dataframe['wlan.fc.type_subtype'] == 44)) &
			 (dataframe['wlan.sa'].isin(clients)) &
			 (dataframe['wlan.fc.pwrmgt'] == 0))
		]
		ndf_count = len(_df_episode_3)

		# check metric
		cause = str(False)
		if beacon_count == 0 or beacon_interval_count > 8 or (ack_count == 0 and ndf_count > 0):
			cause = str(True)

		# append data to output dictionary
		output['beacon.count'].append(beacon_count)
		output['beacon.interval'].append(beacon_interval_count)
		output['ack.count'].append(ack_count)
		output['ndf.count'].append(ndf_count)
		output['cause.beaconloss'].append(cause)
	return output


def rbs__unsuccessful_assoc_auth_reassoc_deauth(dataframe, episode_min_idx, episode_max_idx, clients: list):
	output = {
		'failure.assoc.count': [],
		'cause.unsuccessAssoc': []
	}

	for episode_idx in range(episode_min_idx, episode_max_idx + 1):
		# filter:
		#   - episode index = `episode_idx`
		#   - packet type = `deauth`
		#   - destination address should be in `clients`
		_df_episode_1 = dataframe[
			((dataframe['episode'] == episode_idx) &
			 (dataframe['wlan.fc.type_subtype'] == 12) &
			 (dataframe['wlan.da'].isin(clients)))
		]
		deauth_count = len(_df_episode_1)

		# filter:
		#   - episode index = `episode_idx`
		#   - packet type = `1` or `3`
		#   - `status code` != 0
		#   - destination address should be in `clients`
		_df_episode_2 = dataframe[
			((dataframe['episode'] == episode_idx) &
			 ((dataframe['wlan.fc.type_subtype'] == 1) | (dataframe['wlan.fc.type_subtype'] == 3)) &
			 (dataframe['wlan_mgt.fixed.status_code'] != 0) &
			 (dataframe['wlan.da'].isin(clients)))
		]
		failure_assoc_count = len(_df_episode_2)

		# check metric
		cause = str(False)
		if deauth_count > 0 and failure_assoc_count == 0:
			cause = str(True)

		# append data to output dictionary
		output['failure.assoc.count'].append(failure_assoc_count)
		output['cause.unsuccessAssoc'].append(cause)
	return output


def rbs__successful_assoc_auth_reassoc_deauth(dataframe, episode_min_idx, episode_max_idx, clients: list):
	output = {
		'success.assoc.count': [],
		'cause.successAssoc': []
	}

	for episode_idx in range(episode_min_idx, episode_max_idx + 1):
		# filter:
		#   - episode index = `episode_idx`
		#   - packet type = `deauth`
		#   - destination address should be in `clients`
		_df_episode_1 = dataframe[
			((dataframe['episode'] == episode_idx) &
			 (dataframe['wlan.fc.type_subtype'] == 12) &
			 (dataframe['wlan.da'].isin(clients)))
		]
		deauth_count = len(_df_episode_1)

		# filter:
		#   - episode index = `episode_idx`
		#   - packet type = `1` or `3`
		#   - `status code` = 0
		#   - destination address should be in `clients`
		_df_episode_2 = dataframe[
			((dataframe['episode'] == episode_idx) &
			 ((dataframe['wlan.fc.type_subtype'] == 1) | (dataframe['wlan.fc.type_subtype'] == 3)) &
			 (dataframe['wlan_mgt.fixed.status_code'] == 0) &
			 (dataframe['wlan.da'].isin(clients)))
		]
		success_assoc_count = len(_df_episode_2)

		# check metric
		cause = str(False)
		if deauth_count == 0 and success_assoc_count > 0:
			cause = str(True)

		# append data to output dictionary
		output['success.assoc.count'].append(success_assoc_count)
		output['cause.successAssoc'].append(cause)
	return output


def rbs__class_3_frames(dataframe, episode_min_idx, episode_max_idx):
	class_3_frames_list = [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 26, 24, 25, 13, 14]

	output = {
		'class3frames.count': [],
		'cause.class3': []
	}

	for episode_idx in range(episode_min_idx, episode_max_idx + 1):
		# filter:
		#   - episode index = `episode_idx`
		#   - packet type should be in `class_3_frames_list`
		_df_episode = dataframe[
			((dataframe['episode'] == episode_idx) &
			 (dataframe['wlan.fc.type_subtype'].isin(class_3_frames_list)))
		]

		# calculate metrics
		metric = len(_df_episode)

		# check metric
		cause = str(False)
		if metric > 0:
			cause = str(True)

		# append data to output dictionary
		output['class3frames.count'].append(metric)
		output['cause.class3'].append(cause)
	return output


def define_episodes_from_frames(dataframe: pd.DataFrame, raw_csv_file):
	"""
	Bundle frames into episodes by assigning a `episode` field to each frame.
	"""

	# filter: packet type = `probe request`
	_df_preqs = dataframe[dataframe['wlan.fc.type_subtype'] == 4]

	if len(_df_preqs) == 0:
		print("ERROR! {:s} - (define_episodes_from_frames) `_df_preqs` length is 0!!!".format(raw_csv_file))
		return None

	# reverse the probe request dataframe
	_df_reverse: pd.DataFrame = _df_preqs.iloc[::-1]

	# calculate episode windows
	last_epoch = 0
	episode_start_epochs = list()
	for idx, series in _df_reverse.iterrows():
		current_epoch = float(series['frame.time_epoch'])
		if abs(last_epoch - current_epoch) > 1:
			episode_start_epochs.append(current_epoch)
		last_epoch = current_epoch
	episode_start_epochs.sort()

	if len(episode_start_epochs) == 0:
		print("ERROR! {:s} - (define_episodes_from_frames) `episode_start_epochs` length is 0!!!".format(raw_csv_file))
		return None

	# add `episode` field to each frame
	last_epoch = 0
	for episode_index, current_epoch in enumerate(episode_start_epochs):
		dataframe.loc[
			(dataframe['frame.time_epoch'] <= current_epoch) & (dataframe['frame.time_epoch'] > last_epoch),
			'episode'
		] = episode_index
		last_epoch = current_epoch

	# make sure all episodes have non negative indexes
	# this also removes frames that could not be assigned to any episode
	dataframe = dataframe[(dataframe['episode'] > -1)]
	return dataframe


def filter_frames(dataframe: pd.DataFrame, clients: list, raw_csv_file):
	"""
	Filter out the rows (frames) that are not relevant to the process.
	"""

	# Filter
	#   - source address in clients
	#   - destination address in clients
	#   - transmitter address in clients
	#   - receiver address in clients
	#   - packet type is `beacon` TODO: verify
	_df = dataframe[
		((dataframe['wlan.sa'].isin(clients)) |
		 (dataframe['wlan.da'].isin(clients)) |
		 (dataframe['wlan.ra'].isin(clients)) |
		 (dataframe['wlan.ta'].isin(clients)) |
		 (dataframe['wlan.fc.type_subtype'] == 8))
	]

	if len(_df) == 0:
		print("ERROR! {:s} - (filter_frames) `_df` length is 0!!!".format(raw_csv_file))
		return None

	return _df


def find_all_client_mac_addresses(dataframe):
	"""
	Returns a list of all the client mac addresses present in the csv dataframe.
	"""

	client_mac_addresses = set()
	client_mac_addresses.update(set(dataframe['wlan.sa'][dataframe['wlan.sa'].notna()].unique()))
	client_mac_addresses.update(set(dataframe['wlan.da'][dataframe['wlan.da'].notna()].unique()))
	client_mac_addresses.update(set(dataframe['wlan.ta'][dataframe['wlan.ta'].notna()].unique()))
	client_mac_addresses.update(set(dataframe['wlan.ra'][dataframe['wlan.ra'].notna()].unique()))

	# convert to list
	client_mac_addresses = list(client_mac_addresses)
	# sort for printing
	# client_mac_addresses.sort()
	return client_mac_addresses


# #############################################################################

# get current directory
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
# raw csv directory
RAW_CSV_FILES_DIR = os.path.join(PROJECT_DIR, 'raw_csv_files')
# analyzed csv directory
ANALYZED_CSV_FILES_DIR = os.path.join(PROJECT_DIR, 'analyzed_csv_files')

# Supported Extensions - only files with supported extensions shall be read
SUPPORTED_EXTS = ['.csv', ]

# Process for clients (mac addresses here!)
# set PROCESS_ALL_CLIENTS = `True` to process for all the clients
PROCESS_ALL_CLIENTS = True
CLIENTS = []
CLIENTS = [str(x).lower() for x in CLIENTS]


def prepare_environment():
	# create directories if they don't exist
	if not os.path.exists(RAW_CSV_FILES_DIR) or not os.path.isdir(RAW_CSV_FILES_DIR):
		os.mkdir(RAW_CSV_FILES_DIR)
	if not os.path.exists(ANALYZED_CSV_FILES_DIR) or not os.path.isdir(ANALYZED_CSV_FILES_DIR):
		os.mkdir(ANALYZED_CSV_FILES_DIR)

	# make sure RAW_CSV_FILES_DIR is not empty
	if len(os.listdir(RAW_CSV_FILES_DIR)) == 0:
		print('"{:s}" is empty! Please create raw csv files using `pcaptocsv.py` and try again!'.format(
			RAW_CSV_FILES_DIR))
		exit(0)
	# make sure ANALYZED_CSV_FILES_DIR is empty
	if len(os.listdir(ANALYZED_CSV_FILES_DIR)) != 0:
		print('"{:s}" is not empty! Please empty the directory and try again!'.format(ANALYZED_CSV_FILES_DIR))
		exit(0)


def get_raw_csv_file_names():
	"""
	Read all the file names present in the RAW_CSV_FILES_DIR
	"""

	raw_csv_file_names = list()
	for file in os.listdir(RAW_CSV_FILES_DIR):
		if os.path.splitext(file)[1] in SUPPORTED_EXTS:
			raw_csv_file_names.append(file)

	# sort so that we always read in a predefined order
	# key: smallest file first
	raw_csv_file_names.sort(key = lambda f: os.path.getsize(os.path.join(RAW_CSV_FILES_DIR, f)))
	return raw_csv_file_names


def read_raw_csv_file(filepath, error_bad_lines: bool = False, warn_bad_lines: bool = True):
	"""
	Read csv file using `pandas` and convert it to a `dataframe`.
	Applies filters and other optimizations while reading to sanitize the data as much as possible.

	:param filepath: path to the csv file
	:param error_bad_lines: raise an error for malformed csv line (False = drop bad lines)
	:param warn_bad_lines: raise a warning for malformed csv line (only if `error_bad_lines` is False)
	:return: dataframe object
	"""

	csv_dataframe = pd.read_csv(
		filepath_or_buffer = filepath,
		sep = ',',  # comma separated values (default)
		header = 0,  # use first row as column_names
		index_col = None,  # do not use any column to index
		skipinitialspace = True,  # skip any space after delimiter
		na_values = ['', ],  # values to consider as `not available`
		na_filter = True,  # detect `not available` values
		skip_blank_lines = True,  # skip any blank lines in the file
		float_precision = 'high',
		error_bad_lines = error_bad_lines,
		warn_bad_lines = warn_bad_lines
	)

	# sort the dataframe by `frame.number`
	#   usually file is sorted by default, but just make sure
	csv_dataframe.sort_values(
		by = 'frame.number',
		axis = 0,
		ascending = True,
		inplace = True,
		na_position = 'last'
	)

	return csv_dataframe


def analyze_raw_csv_file(index: int, raw_csv_name: str):
	"""
	Analyze a raw csv file and generate a processed csv file that can be used for machine learning.
	"""

	# raw csv file
	raw_csv_file = os.path.join(RAW_CSV_FILES_DIR, raw_csv_name)
	# read the raw csv file
	dataframe = read_raw_csv_file(raw_csv_file)
	# print("1. read:", dataframe.shape)

	# create a clients list
	if PROCESS_ALL_CLIENTS:
		clients = find_all_client_mac_addresses(dataframe)
	else:
		clients = CLIENTS

	# ### Processing ###

	# 1. filter frames (based on clients)
	dataframe = filter_frames(dataframe, clients, raw_csv_file)
	if dataframe is None:
		return
	# print("2. filter:", dataframe.shape)

	# 2. define episodes
	dataframe = define_episodes_from_frames(dataframe, raw_csv_file)
	if dataframe is None:
		return
	# print("3. define episodes:", dataframe.shape)

	# episode count/bounds
	episode_idx_range_min = int((dataframe.head(1))['episode'])
	episode_idx_range_max = int((dataframe.tail(1))['episode'])
	# print("episode range:", episode_idx_range_min, episode_idx_range_max)

	# 3. apply proper tags
	tag1 = rbs__low_rssi(dataframe, episode_idx_range_min, episode_idx_range_max, clients)
	# print("lowrssi", tag1)
	tag2 = rbs__data_frame_loss(dataframe, episode_idx_range_min, episode_idx_range_max, clients)
	# print("data frame loss", tag2)
	tag3 = rbs__power_state_low_to_high_v1(dataframe, episode_idx_range_min, episode_idx_range_max, clients)
	# print("power state low to high v1", tag3)
	tag4 = rbs__power_state_low_to_high_v2(dataframe, episode_idx_range_min, episode_idx_range_max, clients)
	# print("power state low to high v2", tag4)
	tag5 = rbs__ap_deauth(dataframe, episode_idx_range_min, episode_idx_range_max, clients)
	# print("ap deauth", tag5)
	tag6 = rbs__client_deauth(dataframe, episode_idx_range_min, episode_idx_range_max, clients)
	# print("client deauth", tag6)
	tag7 = rbs__beacon_loss(dataframe, episode_idx_range_min, episode_idx_range_max, clients)
	# print("beacon loss", tag7)
	tag8 = rbs__unsuccessful_assoc_auth_reassoc_deauth(dataframe, episode_idx_range_min, episode_idx_range_max, clients)
	# print("unsuccessful association", tag8)
	tag9 = rbs__successful_assoc_auth_reassoc_deauth(dataframe, episode_idx_range_min, episode_idx_range_max, clients)
	# print("successful association", tag9)
	tag10 = rbs__class_3_frames(dataframe, episode_idx_range_min, episode_idx_range_max)
	# print("class 3 frames", tag10)

	# 4. Save output
	final_result = merge_dictionaries(tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10)

	final_result['cause'] = ['' for _ in range(len(final_result['cause.apsideproc']))]
	drops = []
	for key, value in final_result.items():
		if 'cause.' in key:
			for i in range(0, len(value)):
				if 'True' in value[i]:
					if final_result['cause'][i] is None:
						final_result['cause'][i] = get_tag_for_cause(key)
					else:
						final_result['cause'][i] += get_tag_for_cause(key)
				else:
					final_result['cause'][i] += ''
			drops.append(key)

	output_dataframe = pd.DataFrame(final_result)
	for i in drops:
		output_dataframe = output_dataframe.drop(i, axis = 1)

	# store final output
	output_csvname = os.path.basename(raw_csv_file)
	output_csvfile = os.path.join(ANALYZED_CSV_FILES_DIR, output_csvname)
	output_dataframe.to_csv(output_csvfile, sep = ',')


def analyze_raw_csv_files(raw_csv_file_names: list, use_multithreading: bool = False):
	"""
	Analyze the raw csv files and generate processed csv files that can be used for machine learning.
	"""

	threads = list()
	for idx, raw_csv_name in enumerate(raw_csv_file_names):
		# use multithreading
		if use_multithreading:
			# create a thread for each file
			thread = threading.Thread(target = analyze_raw_csv_file, args = (idx, raw_csv_name))
			print('starting thread for file: {:s}...'.format(raw_csv_name))
			threads.append(thread)
			thread.start()
		else:
			analyze_raw_csv_file(idx, raw_csv_name)

	# if using multi-threading wait for all threads to finish
	# else - this list should be empty, so instantly return
	for thread in threads:
		thread.join()


def main():
	prepare_environment()
	raw_csv_file_names = get_raw_csv_file_names()
	analyze_raw_csv_files(raw_csv_file_names, use_multithreading = True)


if __name__ == '__main__':
	main()
	pass
