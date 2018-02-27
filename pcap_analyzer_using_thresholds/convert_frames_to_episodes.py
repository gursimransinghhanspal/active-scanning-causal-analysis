import enum
import os

import pandas as pd

import pcap_analyzer_using_thresholds.devices as devices


class RBSCauses(enum.Enum):
	low_rssi = 'd'
	data_frame_loss = 'i'
	power_state = 'e'
	power_state_v2 = 'f'
	ap_side_procedure = 'g'
	client_deauth = 'm'
	beacon_loss = 'h'
	unsuccessful_association = 'a'
	successful_association = 'c'
	class_3_frames = 'b'


class EpisodeFeatures(enum.Enum):
	rssi__mean = 'rssi__mean'
	rssi__sd = 'rssi__sd'
	frame__loss_rate = 'frame__loss_rate'
	frame__frequency = 'frame__frequency'
	ap_deauth__count = 'ap_deauth__count'
	client_deauth__count = 'client_deauth__count'
	beacon__count = 'beacon__count'
	max_consecutive_beacons__count = 'max_consecutive_beacons__count'
	ack__count = 'ack__count'
	null_dataframe__count = 'null_dataframe__count'
	failure_assoc__count = 'failure_assoc__count'
	success_assoc__count = 'success_assoc__count'
	class_3_frames__count = 'class_3_frames__count'


class EpisodeProperties(enum.Enum):
	start__time_epoch = 'start__time_epoch'
	end__time_epoch = 'end__time_epoch'
	episode_duration = 'episode_duration'
	associated_client = 'associated_client'


def get_skeleton_features_dictionary(default_to_list = False):
	"""
	Returns a dictionary with all the episode features as keys
	All the values are set by default to 0
	"""

	skeleton_features = dict()
	for _feature in EpisodeFeatures:
		if default_to_list:
			skeleton_features[_feature] = list()
		else:
			skeleton_features[_feature] = 0

	return skeleton_features


def get_skeleton_properties_dictionary(default_to_list = False):
	"""
	Returns a dictionary all the episode properties as keys.
	All the values are set by default to ''
	"""

	skeleton_properties = dict()
	for _property in EpisodeProperties:
		if default_to_list:
			skeleton_properties[_property] = list()
		else:
			skeleton_properties[_property] = ''

	return skeleton_properties


def get_skeleton_rbs_causes_dictionary():
	"""
	Returns a dictionary all the rbs causes as keys.
	All the values are set by default to False
	"""

	skeleton_causes = dict()
	for _cause in RBSCauses:
		skeleton_causes[_cause] = False
	return skeleton_causes


def get_output_column_order():
	features = [item.value for item in EpisodeFeatures]
	features.sort()

	properties = [item.value for item in EpisodeProperties]
	properties.sort()

	output = list()
	output.extend(features)
	output.extend(properties)
	return output


def define_episodes_from_frames(dataframe: pd.DataFrame):
	"""
	Bundle frames into episodes by assigning a `episode_index` field to each frame.
	Returns:
		1. dataframe with 'episode_index' field
		2. episode__count
		3. episode__indexes
	"""

	# filter: packet type = `probe request`
	_df_preqs = dataframe[dataframe['wlan.fc.type_subtype'] == 4]
	# sort the dataframe by `frame.time_epoch`
	_df_preqs.sort_values(
		by = 'frame.time_epoch',
		axis = 0,
		ascending = True,
		inplace = True,
		na_position = 'last'
	)

	if len(_df_preqs) == 0:
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
		return None

	# add `episode_index` field to each frame
	last_epoch = 0
	for episode_index, current_epoch in enumerate(episode_start_epochs):
		dataframe.loc[
			(dataframe['frame.time_epoch'] <= current_epoch) & (dataframe['frame.time_epoch'] > last_epoch),
			'episode_index'
		] = episode_index
		last_epoch = current_epoch

	# make sure all episodes have non negative indexes
	# this also removes frames that could not be assigned to any episode
	dataframe = dataframe[(dataframe['episode_index'] > -1)]
	dataframe['episode_index'] = dataframe['episode_index'].astype(int)

	# list of episode indexes
	ep_indexes = list(dataframe['episode_index'].unique())

	return dataframe, len(ep_indexes), ep_indexes


def filter_out_irrelevant_frames(dataframe: pd.DataFrame, clients: list, access_points: list = None):
	"""
	Filter out the rows (frames) that are not relevant to the process.
	"""

	# Filter
	#   - source address in clients
	#   OR
	#   - destination address in clients
	#   OR
	#   - transmitter address in clients
	#   OR
	#   - receiver address in clients
	#   OR
	#   - packet type is `beacon` AND the source address or transmitter address is in access points
	if access_points is not None:
		_df = dataframe[
			((dataframe['wlan.sa'].isin(clients)) |
			 (dataframe['wlan.da'].isin(clients)) |
			 (dataframe['wlan.ra'].isin(clients)) |
			 (dataframe['wlan.ta'].isin(clients)) |
			 ((dataframe['wlan.fc.type_subtype'] == 8) &
			  ((dataframe['wlan.sa'].isin(access_points)) | (dataframe['wlan.ta'].isin(access_points)))))
		]
	else:
		_df = dataframe[
			((dataframe['wlan.sa'].isin(clients)) |
			 (dataframe['wlan.da'].isin(clients)) |
			 (dataframe['wlan.ra'].isin(clients)) |
			 (dataframe['wlan.ta'].isin(clients)) |
			 (dataframe['wlan.fc.type_subtype'] == 8))
		]

	if len(_df) == 0:
		return None
	return _df


def filter_client_frames(dataframe: pd.DataFrame, client_mac: str):
	"""
	Filter out the rows (frames) that do not associate with the given client.
	"""

	# Filter
	#   - source address == `client_mac`
	#   OR
	#   - destination address == `client_mac`
	#   OR
	#   - transmitter address == `client_mac`
	#   OR
	#   - receiver address == `client_mac`
	#   OR
	#   - packet type is `beacon`
	_df = dataframe[
		((dataframe['wlan.sa'] == client_mac) |
		 (dataframe['wlan.da'] == client_mac) |
		 (dataframe['wlan.ra'] == client_mac) |
		 (dataframe['wlan.ta'] == client_mac) |
		 (dataframe['wlan.fc.type_subtype'] == 8))
	]

	if len(_df) == 0:
		return None
	return _df


def find_all_client_mac_addresses(dataframe):
	"""
	Returns a list of all the client mac addresses present in the csv dataframe.
	"""

	# look at only probe requests
	_preq_df = dataframe[dataframe['wlan.fc.type_subtype'] == 4]

	client_mac_addresses = set()
	client_mac_addresses.update(set(_preq_df['wlan.sa'][_preq_df['wlan.sa'].notna()].unique()))
	client_mac_addresses.update(set(_preq_df['wlan.da'][_preq_df['wlan.da'].notna()].unique()))
	client_mac_addresses.update(set(_preq_df['wlan.ta'][_preq_df['wlan.ta'].notna()].unique()))
	client_mac_addresses.update(set(_preq_df['wlan.ra'][_preq_df['wlan.ra'].notna()].unique()))

	# remove `broadcast`
	client_mac_addresses.remove('ff:ff:ff:ff:ff:ff')

	# convert to list
	client_mac_addresses = list(client_mac_addresses)
	client_mac_addresses.sort()
	return client_mac_addresses


def compute_episode_characteristics(ep_dataframe: pd.DataFrame, the_client: str):
	"""
	Computes all the features required by the machine learning model for an episode dataframe
	Computes all the episode properties required for processing the output of ML model
	"""

	out_features = get_skeleton_features_dictionary()
	out_properties = get_skeleton_properties_dictionary()

	# Filter
	#   - either `source addr` or `transmitter addr` belongs to the client
	client_origin_df = ep_dataframe[
		((ep_dataframe['wlan.sa'] == the_client) |
		 (ep_dataframe['wlan.ta'] == the_client))
	]

	def __f1():
		"""
		1. EpisodeFeatures.rssi__mean
		2. EpisodeFeatures.rssi__sd
		"""

		_rssi_mean = client_origin_df['radiotap.dbm_antsignal'].mean()
		_rssi_stddev = client_origin_df['radiotap.dbm_antsignal'].std()
		return _rssi_mean, _rssi_stddev

	def __f2():
		"""
		1. EpisodeFeatures.frame__loss_rate
		"""

		_df_retry_true = client_origin_df[
			(client_origin_df['wlan.fc.retry'] == 1)
		]
		_df_retry_false = client_origin_df[
			(client_origin_df['wlan.fc.retry'] == 0)
		]

		_num_true = len(_df_retry_true)
		_num_false = len(_df_retry_false)

		if _num_true + _num_false > 0:
			_loss_rate = float(_num_true) / float(_num_true + _num_false)
		else:
			_loss_rate = -1  # could not calculate

		return _loss_rate

	def __f3():
		"""
		1. EpisodeFeatures.frame__frequency
		"""

		# no frames in client source dataframe
		if len(client_origin_df) == 0:
			return 0

		_, _, _ep_duration = __p1()
		_num_frames = len(client_origin_df)

		_frequency = -1
		if _num_frames >= 0 and _ep_duration > 0:
			_frequency = float(_num_frames) / float(_ep_duration)

		return _frequency

	def __f4():
		"""
		1. EpisodeFeatures.ap_deauth__count
		"""

		# Filter:
		#   - packet type = `12` (deauth)
		#   - destination should be `the client`
		_deauth_ap_df = ep_dataframe[
			((ep_dataframe['wlan.fc.type_subtype'] == 12) &
			 (ep_dataframe['wlan.da'] == the_client))
		]

		_ap_deauth_count = len(_deauth_ap_df)
		return _ap_deauth_count

	def __f5():
		"""
		1. EpisodeFeatures.client_deauth__count
		"""

		# filter:
		#   - packet type = `12` (deauth)
		#   - source should be `the client`
		_deauth_client_df = ep_dataframe[
			((ep_dataframe['wlan.fc.type_subtype'] == 12) &
			 (ep_dataframe['wlan.sa'] == the_client))
		]

		_client_deauth_count = len(_deauth_client_df)
		return _client_deauth_count

	def __f6():
		"""
		1. EpisodeFeatures.beacon__count
		2. EpisodeFeatures.max_consecutive_beacons__count
		3. EpisodeFeatures.ack__count
		4. EpisodeFeatures.null_dataframe__count
		"""

		# filter:
		#   - packet type = `8` (beacon)
		_beacon_df = ep_dataframe[
			(ep_dataframe['wlan.fc.type_subtype'] == 8)
		]

		# beacon count
		_beacon_count = len(_beacon_df)

		# max consecutive beacon count (earlier `beacon interval count`)
		#   - defines maximum number of consecutive beacons in the episodes
		#   - consecutive == interval between packets < 105 milliseconds
		_max_consecutive_beacon_count = 0
		_beacon_interval_count = 0
		if _beacon_count > 1:
			_previous_epoch = float(_beacon_df.head(1)['frame.time_epoch'])
			_beacon_df = _beacon_df.iloc[1:]

			for index, frame in _beacon_df.iterrows():
				_current_epoch = float(frame['frame.time_epoch'])
				_delta_time = _previous_epoch - _current_epoch

				if _delta_time > 0.105:
					_beacon_interval_count += 1
				else:
					_beacon_interval_count = 0

				_max_consecutive_beacon_count = max(_max_consecutive_beacon_count, _beacon_interval_count)
				_previous_epoch = _current_epoch

		# filter:
		#   - packet type = `29` (ack)
		#   - receiver should be `the client`
		_ack_df = ep_dataframe[
			((ep_dataframe['wlan.fc.type_subtype'] == 29) &
			 (ep_dataframe['wlan.ra'] == the_client))
		]
		_ack_count = len(_ack_df)

		# filter:
		#   - packet type = `36` or `44` (null, qos null)
		#   - source should be in clients
		#   - power management bit = 0
		_null_df = ep_dataframe[
			(((ep_dataframe['wlan.fc.type_subtype'] == 36) | (ep_dataframe['wlan.fc.type_subtype'] == 44)) &
			 (ep_dataframe['wlan.sa'] == the_client) &
			 (ep_dataframe['wlan.fc.pwrmgt'] == 0))
		]
		_null_dataframe_count = len(_null_df)
		return _beacon_count, _max_consecutive_beacon_count, _ack_count, _null_dataframe_count

	def __f7():
		"""
		1. EpisodeFeatures.failure_assoc__count
		"""

		# filter:
		#   - packet type = `1` or `3` (association response, re-association response)
		#   - `status code` != 0
		#   - destination should be `the client`
		_assoc_reassoc_failure_response_df = ep_dataframe[
			(((ep_dataframe['wlan.fc.type_subtype'] == 1) | (ep_dataframe['wlan.fc.type_subtype'] == 3)) &
			 (ep_dataframe['wlan_mgt.fixed.status_code'] != 0) &
			 (ep_dataframe['wlan.da'] == the_client))
		]
		_failure_assoc_reassoc_count = len(_assoc_reassoc_failure_response_df)
		return _failure_assoc_reassoc_count

	def __f8():
		"""
		1. EpisodeFeatures.success_assoc__count
		"""

		# filter:
		#   - packet type = `1` or `3` (association response, re-association response)
		#   - `status code` = 0
		#   - destination should be `the client`
		_assoc_reassoc_success_response_df = ep_dataframe[
			(((ep_dataframe['wlan.fc.type_subtype'] == 1) | (ep_dataframe['wlan.fc.type_subtype'] == 3)) &
			 (ep_dataframe['wlan_mgt.fixed.status_code'] == 0) &
			 (ep_dataframe['wlan.da'] == the_client))
		]
		_success_assoc_reassoc_count = len(_assoc_reassoc_success_response_df)
		return _success_assoc_reassoc_count

	def __f9():
		"""
		1. EpisodeFeatures.class_3_frames__count
		"""

		class_3_frames_list = [
			32,  # type 2 (data), data
			33,  # type 2 (data), data + cf_ack
			34,  # type 2 (data), data + cf_poll
			35,  # type 2 (data), data + cf_ack + cf_poll
			36,  # type 2 (data), null
			37,  # type 2 (data), cf_ack
			38,  # type 2 (data), cf_poll
			39,  # type 2 (data), cf_ack + cf_poll
			40,  # type 2 (data), QoS data
			41,  # type 2 (data), QoS data + cf_ack
			42,  # type 2 (data), QoS data + cf_poll
			43,  # type 2 (data), QoS data + cf_ack + cf_poll
			44,  # type 2 (data), QoS null
			46,  # type 2 (data), QoS + cf_poll (no data)
			47,  # type 2 (data), Qos + cf_ack (no data)
			26,  # type 1 (control), ps_poll
			24,  # type 1 (control), block ack request
			25,  # type 1 (control), block ack
			13,  # type 0 (management), action
			14  # type 0 (management), reserved
		]

		# filter:
		#   - packet subtype in `class_3_frames_list`
		_class_3_df = ep_dataframe[
			(ep_dataframe['wlan.fc.type_subtype'].isin(class_3_frames_list))
		]
		_class_3_frames_count = len(_class_3_df)

		return _class_3_frames_count

	def __p1():
		"""
		1. EpisodeProperties.start__time_epoch
		2. EpisodeProperties.end__time_epoch
		3. EpisodeProperties.episode_duration
		"""

		_ep_start_epoch = float(ep_dataframe.head(1)['frame.time_epoch'])
		_ep_end_epoch = float((ep_dataframe.tail(1))['frame.time_epoch'])
		_ep_duration = float(_ep_end_epoch - _ep_start_epoch)
		return _ep_start_epoch, _ep_end_epoch, _ep_duration

	def __p2():
		"""
		1. EpisodeProperties.associated_client
		"""
		return the_client

	out_features[EpisodeFeatures.rssi__mean], out_features[EpisodeFeatures.rssi__sd] = __f1()
	out_features[EpisodeFeatures.frame__loss_rate] = __f2()
	out_features[EpisodeFeatures.frame__frequency] = __f3()
	out_features[EpisodeFeatures.ap_deauth__count] = __f4()
	out_features[EpisodeFeatures.client_deauth__count] = __f5()
	out_features[EpisodeFeatures.beacon__count], out_features[EpisodeFeatures.max_consecutive_beacons__count], \
	out_features[EpisodeFeatures.ack__count], out_features[EpisodeFeatures.null_dataframe__count] = __f6()
	out_features[EpisodeFeatures.failure_assoc__count] = __f7()
	out_features[EpisodeFeatures.success_assoc__count] = __f8()
	out_features[EpisodeFeatures.class_3_frames__count] = __f9()

	out_properties[EpisodeProperties.start__time_epoch], out_properties[EpisodeProperties.end__time_epoch], \
	out_properties[EpisodeProperties.episode_duration] = __p1()
	out_properties[EpisodeProperties.associated_client] = __p2()

	return out_features, out_properties


def assign_rule_based_system_tags_to_episodes(episodes_df: pd.DataFrame):
	"""
	Assigns a 'cause' field to each row of the dataframe with tags for each cause inferred
	by the rule based checks.
	"""

	def __low_rssi(episode):
		"""
		For every episode, calculate `mean` and `standard deviation` for rssi value.
		check: `mean` < -72dB and `std dev` > 12dB
		"""

		if episode[EpisodeFeatures.rssi__mean.value] < -72 and episode[EpisodeFeatures.rssi__sd.value] > 12:
			return True
		return False

	def __data_frame_loss(episode):
		"""
		use `fc.retry` field
		check: #(fc.retry == 1)/#(fc.retry == 1 || fc.retry == 0) > 0.5
		"""

		if episode[EpisodeFeatures.frame__loss_rate.value] > 0.5:
			return True
		return False

	def __power_state_low_to_high_v1(episode):
		"""
		calculate number of frames per second.
		check: if #fps > 2
		"""

		_frame_frequency = episode[EpisodeFeatures.frame__frequency.value]
		if _frame_frequency == -1:
			return False
		elif _frame_frequency > 2:
			return True
		return False

	def __power_state_low_to_high_v2(episode):
		"""
		calculate number of frames per second.
		check: if #fps <= 2
		"""

		_frame_frequency = episode[EpisodeFeatures.frame__frequency.value]
		if _frame_frequency == -1:
			return False
		elif _frame_frequency <= 2:
			return True
		return False

	def __ap_deauth(episode):
		"""
		check for deauth packet from ap
		deauth: fc.type_subtype == 12
		"""

		if episode[EpisodeFeatures.ap_deauth__count.value] > 0:
			return True
		return False

	def __client_deauth(episode):
		"""
		check for deauth packet from client
		deauth: fc.type_subtype == 12
		"""

		if episode[EpisodeFeatures.client_deauth__count.value] > 0:
			return True
		return False

	def __beacon_loss(episode):
		"""
		beacon count is 0 or
		if beacon interval > 105ms for 7 consecutive beacons or
		count(wlan.sa = client and type_subtype = 36|44 and pwrmgt = 0) > 0 and count(wlan.ra = client && type_subtype = 29)
		"""

		if episode[EpisodeFeatures.beacon__count.value] == 0 or \
				episode[EpisodeFeatures.max_consecutive_beacons__count.value] >= 8 or \
				(episode[EpisodeFeatures.ack__count.value] == 0 and
				 episode[EpisodeFeatures.null_dataframe__count.value] > 0):
			return True
		return False

	def __unsuccessful_assoc_auth_reassoc_deauth(episode):
		if episode[EpisodeFeatures.ap_deauth__count.value] > 0 and \
				episode[EpisodeFeatures.failure_assoc__count.value] == 0:
			return True
		return False

	def __successful_assoc_auth_reassoc_deauth(episode):
		if episode[EpisodeFeatures.ap_deauth__count.value] == 0 and \
				episode[EpisodeFeatures.success_assoc__count.value] > 0:
			return True
		return False

	def __class_3_frames(episode):
		if episode[EpisodeFeatures.class_3_frames__count.value] > 0:
			return True
		return False

	for idx, _episode in episodes_df.iterrows():

		cause_str = ''
		if __low_rssi(_episode):
			cause_str += RBSCauses.low_rssi.value

		if __data_frame_loss(_episode):
			cause_str += RBSCauses.data_frame_loss.value

		if __power_state_low_to_high_v1(_episode):
			cause_str += RBSCauses.power_state.value

		if __power_state_low_to_high_v2(_episode):
			cause_str += RBSCauses.power_state_v2.value

		if __ap_deauth(_episode):
			cause_str += RBSCauses.ap_side_procedure.value

		if __client_deauth(_episode):
			cause_str += RBSCauses.client_deauth.value

		if __beacon_loss(_episode):
			cause_str += RBSCauses.beacon_loss.value

		if __unsuccessful_assoc_auth_reassoc_deauth(_episode):
			cause_str += RBSCauses.unsuccessful_association.value

		if __successful_assoc_auth_reassoc_deauth(_episode):
			cause_str += RBSCauses.successful_association.value

		if __class_3_frames(_episode):
			cause_str += RBSCauses.class_3_frames.value

		episodes_df.loc[idx, 'rbs__cause_tags'] = cause_str
	return episodes_df


def convert_ep_characteristics_to_dataframe(episode_characteristics: list):
	"""
	Creates a dataframe from a list of 2-tuples containing ep_features and ep_properties
	"""

	# merge all dictionaries into one big dictionary
	output_dictionary = dict()
	for _feature in EpisodeFeatures:
		output_dictionary[_feature.value] = list()
	for _property in EpisodeProperties:
		output_dictionary[_property.value] = list()

	for _features_dict, _properties_dict in episode_characteristics:
		for _feature in EpisodeFeatures:
			output_dictionary[_feature.value].append(_features_dict[_feature])
		for _property in EpisodeProperties:
			output_dictionary[_property.value].append(_properties_dict[_property])

	# convert to dataframe
	df = pd.DataFrame.from_dict(output_dictionary)
	return df


# #############################################################################

# get current directory
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
# frames csv directory
FRAMES_CSV_FILES_DIR = os.path.join(PROJECT_DIR, 'frames_csv_files')
# processed episode csv directory
PROCESSED_EPISODE_CSV_FILES_DIR = os.path.join(PROJECT_DIR, 'processed_episode_csv_files')

# Supported Extensions - only files with supported extensions shall be read
SUPPORTED_EXTS = ['.csv', ]


def prepare_environment():
	# create directories if they don't exist
	if not os.path.exists(FRAMES_CSV_FILES_DIR) or not os.path.isdir(FRAMES_CSV_FILES_DIR):
		os.mkdir(FRAMES_CSV_FILES_DIR)
	if not os.path.exists(PROCESSED_EPISODE_CSV_FILES_DIR) or not os.path.isdir(PROCESSED_EPISODE_CSV_FILES_DIR):
		os.mkdir(PROCESSED_EPISODE_CSV_FILES_DIR)

	# make sure FRAMES_CSV_FILES_DIR is not empty
	if len(os.listdir(FRAMES_CSV_FILES_DIR)) == 0:
		print('"{:s}" is empty! Please create `frames csv file` and try again!'.format(
			FRAMES_CSV_FILES_DIR))
		exit(0)
	# make sure PROCESSED_EPISODE_CSV_FILES_DIR is empty
	if len(os.listdir(PROCESSED_EPISODE_CSV_FILES_DIR)) != 0:
		print('"{:s}" is not empty! Please empty the directory and try again!'.format(PROCESSED_EPISODE_CSV_FILES_DIR))
		exit(0)


def get_frames_csv_file_names():
	"""
	Read all the file names present in the FRAMES_CSV_FILES_DIR
	"""

	frames_csv_file_names = list()
	for file in os.listdir(FRAMES_CSV_FILES_DIR):
		if os.path.splitext(file)[1] in SUPPORTED_EXTS:
			frames_csv_file_names.append(file)

	# sort so that we always read in a predefined order
	# key: smallest file first
	frames_csv_file_names.sort(key = lambda f: os.path.getsize(os.path.join(FRAMES_CSV_FILES_DIR, f)))
	return frames_csv_file_names


def read_frames_csv_file(filepath, error_bad_lines: bool = False, warn_bad_lines: bool = True):
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

	# sanitize data
	#   - drop not available values
	csv_dataframe.dropna(axis = 0, subset = ['frame.time_epoch', 'radiotap.dbm_antsignal', ], inplace = True)

	# sort the dataframe by `frame.time_epoch`
	csv_dataframe.sort_values(
		by = 'frame.time_epoch',
		axis = 0,
		ascending = True,
		inplace = True,
		na_position = 'last'
	)

	return csv_dataframe


def process_frame_csv_file(frames_csv_name: str, access_points, clients, assign_rbs_tags, separate_client_files):
	"""
	Processes a given frame csv file to generate episode characteristics.

	:param frames_csv_name:
	:param access_points:
	:param clients:
	:param assign_rbs_tags:
	:param separate_client_files:
	:return:
	"""

	# frames csv file
	frames_csv_file = os.path.join(FRAMES_CSV_FILES_DIR, frames_csv_name)
	# read the frames csv file
	main_dataframe = read_frames_csv_file(frames_csv_file)
	print('• Dataframe shape (on read'
	      '):', main_dataframe.shape)

	if clients is None:
		clients = find_all_client_mac_addresses(main_dataframe)

	# all episodes characteristics as list of 2-tuples
	#   - 1. features
	#   - 2. properties
	ep_characteristics_list = list()

	# ### Processing ###
	# 1. keep only relevant frames in memory
	main_dataframe = filter_out_irrelevant_frames(main_dataframe, clients, access_points)
	print('• Dataframe shape (relevance filter):', main_dataframe.shape)

	# 2. for each client...
	for the_client in clients:
		# 2.a. copy the main_dataframe
		dataframe = main_dataframe.copy(deep = True)

		# 2.b. filter frames belonging to the client
		dataframe = filter_client_frames(dataframe, the_client)
		if dataframe is None:
			print('• No relevant frames found for client {:s} -'.format(the_client))
			continue

		# 2.c. define episodes on frames
		result = define_episodes_from_frames(dataframe)
		if result is not None:
			dataframe, ep_count, ep_indexes = result
			print('• Episodes generated for client {:s} -'.format(the_client), ep_count)

			if ep_count == 0:
				continue
		else:
			print('• Episodes generated for client {:s} -'.format(the_client), 0)
			continue

		# 2.d. for each episode...
		for episode_idx in ep_indexes:
			# 2.d.1. get all frames belonging to the episode
			_episode_df = dataframe[
				(dataframe['episode_index'] == episode_idx)
			]
			# 2.d.2. sort the dataframe by `frame.time_epoch`
			_episode_df.sort_values(
				by = 'frame.time_epoch',
				axis = 0,
				ascending = True,
				inplace = True,
				na_position = 'last'
			)

			# 2.d.3. compute episode characteristics
			ep_features, ep_properties = compute_episode_characteristics(_episode_df, the_client)

			# 2.d.4. append to output
			ep_characteristics_list.append((ep_features, ep_properties))

	# 3. make a dataframe from episode characteristics
	ep_characteristics_df = convert_ep_characteristics_to_dataframe(ep_characteristics_list)
	print('• Total episodes generated: {:d}'.format(len(ep_characteristics_df)))
	# 3.a. drop null values, since ML model can't make any sense of this
	ep_characteristics_df.dropna(axis = 0, inplace = True)
	print('• Total episodes generated after dropping null values: {:d}'.format(len(ep_characteristics_df)))

	# 4. (optional) assign tags for causes according to old rule-based-system
	if assign_rbs_tags:
		ep_characteristics_df = assign_rule_based_system_tags_to_episodes(ep_characteristics_df)

	# 5. generate a csv file as an output
	output_column_order = get_output_column_order()
	if assign_rbs_tags:
		output_column_order.append('rbs__cause_tags')

	if separate_client_files:
		for the_client in clients:
			_df = ep_characteristics_df[
				(ep_characteristics_df[EpisodeProperties.associated_client.value] == the_client)
			]
			name, extension = os.path.splitext(os.path.basename(frames_csv_file))
			output_csvname = str.format('{:s}_{:s}{:s}', name, the_client, extension)
			output_csvfile = os.path.join(PROCESSED_EPISODE_CSV_FILES_DIR, output_csvname)
			_df.to_csv(output_csvfile, sep = ',', index = False, columns = output_column_order)
	else:
		output_csvname = os.path.basename(frames_csv_file)
		output_csvfile = os.path.join(PROCESSED_EPISODE_CSV_FILES_DIR, output_csvname)
		ep_characteristics_df.to_csv(output_csvfile, sep = ',', index = False, columns = output_column_order)


def process_frame_csv_files(frames_csv_file_names: list, access_points, clients, assign_rbs_tags, separate_client_files):
	"""
	Run `process_frame_csv_file` for multiple files sequentially.

	:param frames_csv_file_names:
	:param access_points:
	:param clients: `None` -- process all clients
	:param assign_rbs_tags:
	:param separate_client_files:
	:return:
	"""

	for idx, frames_csv_name in enumerate(frames_csv_file_names):
		print('Started processing file: {:s}'.format(frames_csv_name))
		process_frame_csv_file(frames_csv_name, access_points = access_points, clients = clients,
		                       assign_rbs_tags = assign_rbs_tags, separate_client_files = separate_client_files)
		print('-' * 40)
		print()


def main(access_points = None, clients = None, assign_rbs_tags = True, separate_client_files = False):
	prepare_environment()
	frames_csv_file_names = get_frames_csv_file_names()
	process_frame_csv_files(frames_csv_file_names, access_points = access_points, clients = clients,
	                        assign_rbs_tags = assign_rbs_tags, separate_client_files = separate_client_files)


if __name__ == '__main__':
	# disable warnings
	pd.options.mode.chained_assignment = None

	# client devices to process for
	_clients = [
		devices.gursimran_oneplus_one,
	]

	# access points
	_access_points = [
		devices.dheryta_netgear,
	]

	#   - clients = None, to process all clients
	#   - access points = None, to use all beacon frames
	main(clients = None, access_points = None, assign_rbs_tags = False, separate_client_files = False)
