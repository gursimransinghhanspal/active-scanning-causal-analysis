import os

import pandas


def get_tag_for_cause(cause):
	"""
	Associates a `tag` corresponding to every cause. This tag is added to the output csv file.
	:param cause:
	:return:
	"""

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


def merge_dicts(*dict_args):
	result = {}
	for dictionary in dict_args:
		result.update(dictionary)
	return result


'''
for every episode, calculate mean and SD of SSI value
if (mean < -72dBm) and (SD > 12dB)
'''


def low_rssi(df, minEpisode, maxEpisode, client):
	# print('Low RSSI Causal Analysis...')
	output = {'ssi.mean': [], 'ssi.sd': [], 'cause.lowrssi': [], 'start.time': [], 'end.time': [], 'duration.time': []}
	for i in range(minEpisode, maxEpisode + 1):
		dfH = df[(df['episode'] == i)]
		dfE = df[(df['episode'] == i) & ((df['wlan.ta'] == client) | (df['wlan.sa'] == client))]
		ssiMean = dfE['radiotap.dbm_antsignal'].mean()
		ssiSD = dfE['radiotap.dbm_antsignal'].std()
		cause = 'False'
		if (ssiMean < -72 and ssiSD > 12):
			cause = 'True'

		startTime = (dfH.head(1))['frame.time_epoch']
		endTime = (dfH.tail(1))['frame.time_epoch']
		output['start.time'].append(float(startTime))
		output['end.time'].append(float(endTime))
		output['duration.time'].append((float(endTime) - float(startTime)) / 60)
		output['ssi.mean'].append(ssiMean)
		output['ssi.sd'].append(ssiSD)
		output['cause.lowrssi'].append(cause)
	return output


'''
check for fc.retry field
if #(fc.retry == 1)/#(fc.retry == 1 || fc.retry == 0) > 0.5
'''


def dataFrameLosses(df, minEpisode, maxEpisode, client):
	# print('DataFrame Loss Causal Analysis...')
	output = {'frame.lossrate': [], 'cause.dataframeloss': []}
	for i in range(minEpisode, maxEpisode + 1):
		dfE = df[(df['episode'] == i)]

		dfE_a = dfE[(dfE['wlan.fc.retry'] == 1)]
		dfE_b = dfE_a[(dfE_a['wlan.sa'] == client)]
		dfE_b.append(dfE_a[(dfE_a['wlan.ta'] == client)])
		numFCRetry = len(dfE_b)

		dfE_a = dfE[(dfE['wlan.fc.retry'] == 0)]
		dfE_b = dfE_a[(dfE_a['wlan.sa'] == client)]
		dfE_b.append(dfE_a[(dfE_a['wlan.ta'] == client)])
		numFCNoRetry = len(dfE_b)

		# numFCRetry = len(dfE[(dfE['wlan.fc.retry'] == 1) & ((dfE['wlan.sa'] == client) | (dfE['wlan.ta'] ==
		# client))])
		# numFCNoRetry = len(dfE[(dfE['wlan.fc.retry'] == 0) & ((dfE['wlan.sa'] == client) | (dfE['wlan.ta'] ==
		# client))])

		if numFCRetry + numFCNoRetry > 0:
			metric = float(numFCRetry) / float(numFCRetry + numFCNoRetry)
			cause = 'False'
			if (metric > 0.5):
				cause = 'True'

			output['frame.lossrate'].append(metric)
			output['cause.dataframeloss'].append(cause)

		else:
			cause = 'False'
			output['frame.lossrate'].append(-1)
			output['cause.dataframeloss'].append(cause)

	return output


'''
. beacon count is 0 or
. if beacon interval > 105ms for 7 consecutive beacons or
. count(wlan.sa = client and type_subtype = 36|44 and pwrmgt = 0) > 0 and count(wlan.ra = client && type_subtype = 29)
'''


def beaconLoss(df, minEpisode, maxEpisode, client):
	# print('Beacon Loss Causal Analysis...')
	output = {'beacon.count': [], 'beacon.interval': [], 'ack.count': [], 'ndf.count': [], 'cause.beaconloss': []}
	for i in range(minEpisode, maxEpisode + 1):
		dfE = df[(df['episode'] == i) & (df['wlan.fc.type_subtype'] == 8)]
		beaconCount = len(dfE)
		beaconIntervalCount = 0
		if beaconCount > 1:
			prevEpoch = float(dfE.head(1)['frame.time_epoch'])
			dfE = dfE.ix[1:]
			for index, row in dfE.iterrows():
				currentEpoch = float(row['frame.time_epoch'])
				timeDiff = abs(prevEpoch - currentEpoch)
				if timeDiff > 0.105:
					beaconIntervalCount += 1
				else:
					beaconIntervalCount = 0
				prevEpoch = currentEpoch

		dfE2 = df[(df['episode'] == i) & (df['wlan.fc.type_subtype'] == 29) & (df['wlan.ra'] == client)]
		ackCount = len(dfE2)

		dfE3 = df[(df['episode'] == i) & ((df['wlan.fc.type_subtype'] == 36) | (df['wlan.fc.type_subtype'] == 44)) & (
				df['wlan.sa'] == client) & (df['wlan.fc.pwrmgt'] == 0)]
		ndfCount = len(dfE3)

		cause = 'False'
		if (beaconCount == 0 or beaconIntervalCount > 8 or (ackCount == 0 and ndfCount > 0)):
			cause = 'True'

		output['beacon.count'].append(beaconCount)
		output['beacon.interval'].append(beaconIntervalCount)
		output['ack.count'].append(ackCount)
		output['ndf.count'].append(ndfCount)
		output['cause.beaconloss'].append(cause)
	return output


'''
check for deauth packet if found in episode 0, assign to episode 1
deauth: fc.type_subtype == 12
'''


def apDeauth(df, minEpisode, maxEpisode, client):
	# print('AP-side Procedures Causal Analysis...')
	output = {'ap.deauth.count': [], 'cause.apsideproc': []}
	for i in range(minEpisode, maxEpisode + 1):
		dfE = df[(df['episode'] == i) & (df['wlan.fc.type_subtype'] == 12) & (df['wlan.da'] == client)]
		metric = len(dfE)
		cause = 'False'
		if metric > 0:
			cause = 'True'

		output['ap.deauth.count'].append(metric)
		output['cause.apsideproc'].append(cause)
	return output


def clientDeauth(df, minEpisode, maxEpisode, client):
	# print('Client Deauth Causal Analysis...')
	output = {'client.deauth.count': [], 'cause.clientdeauth': []}
	for i in range(minEpisode, maxEpisode + 1):
		dfE = df[(df['episode'] == i) & (df['wlan.fc.type_subtype'] == 12) & (df['wlan.sa'] == client)]
		metric = len(dfE)
		cause = 'False'
		if metric > 0:
			cause = 'True'

		output['client.deauth.count'].append(metric)
		output['cause.clientdeauth'].append(cause)
	return output


'''
calculate number of frames (with wlan.sa or wlan.ta from client) per second, nfps
if nfps > 2
'''


def powerStateLowToHigh(df, minEpisode, maxEpisode, client):
	# print('Power State Low->High Analysis...')
	output = {'frames.persec': [], 'cause.powerstate': []}
	for i in range(minEpisode, maxEpisode + 1):
		dfE = df[(df['episode'] == i) & ((df['wlan.ta'] == client) | (df['wlan.sa'] == client))]

		if len(dfE) == 0:
			output['frames.persec'].append(0)
			output['cause.powerstate'].append('False')
			continue

		startEpoch = dfE.head(1)['frame.time_epoch']
		endEpoch = dfE.tail(1)['frame.time_epoch']

		timeWindow = float(endEpoch) - float(startEpoch)
		numOfFrames = len(dfE)
		metric = -1
		if numOfFrames > 1:
			metric = float(numOfFrames) / float(timeWindow)
		cause = 'False'
		if (metric == -1):
			cause = 'Invalid'
		elif (metric > 2):
			cause = 'True'

		output['frames.persec'].append(metric)
		output['cause.powerstate'].append(cause)
	return output


'''
calculate number of frames (with wlan.sa or wlan.ta from client) per second, nfps
if nfps <= 2
'''


def powerStateLowToHighV2(df, minEpisode, maxEpisode, client):
	# print('Power State Low->High Analysis V2...')
	output = {'cause.powerstateV2': []}
	for i in range(minEpisode, maxEpisode + 1):
		dfE = df[(df['episode'] == i) & ((df['wlan.ta'] == client) | (df['wlan.sa'] == client))]

		if len(dfE) == 0:
			output['cause.powerstateV2'].append('True')
			continue

		startEpoch = dfE.head(1)['frame.time_epoch']
		endEpoch = dfE.tail(1)['frame.time_epoch']
		timeWindow = float(endEpoch) - float(startEpoch)
		numOfFrames = len(dfE)
		metric = -1
		if numOfFrames > 1:
			metric = float(numOfFrames) / float(timeWindow)
		cause = 'False'
		if (metric == -1):
			cause = 'Invalid'
		elif (metric <= 2):
			cause = 'True'

		output['cause.powerstateV2'].append(cause)
	return output


def unsuccessAssocBlah(df, minEpisode, maxEpisode, client):
	# print('Unsuccess Assoc/Auth/Reassoc/deauth...')
	# output = { 'unsuccessAssoc.deauth.count': [], 'failure.assoc.count': [], 'cause.unsuccessAssoc': [] }
	output = {'failure.assoc.count': [], 'cause.unsuccessAssoc': []}
	for i in range(minEpisode, maxEpisode + 1):
		# dfE = df[(df['episode'] == i) & (df['wlan.fc.type_subtype'] == 12) & (df['wlan.da'] == client)]
		# deauthCount = len(dfE)
		#
		# dfE2 = df[(df['episode'] == i) & ((df['wlan.fc.type_subtype'] == 1) | (df['wlan.fc.type_subtype'] == 3)) & (
		#       df['wlan_mgt.fixed.status_code'] != 0) & (df['wlan.da'] == client)]
		# failureAssocCount = len(dfE2)
		#
		# cause = 'False'
		# if (deauthCount > 0 and failureAssocCount == 0):
		#   cause = 'True'

		# output['unsuccessAssoc.deauth.count'].append(deauthCount)
		# output['failure.assoc.count'].append(failureAssocCount)
		output['failure.assoc.count'].append(0)
		# output['cause.unsuccessAssoc'].append(cause)
		output['cause.unsuccessAssoc'].append('False')
	return output


def successAssocBlah(df, minEpisode, maxEpisode, client):
	# print('Success Assoc/Auth/Reassoc/deauth...')
	# output = { 'successAssoc.deauth.count': [], 'success.assoc.count': [], 'cause.successAssoc': [] }
	output = {'success.assoc.count': [], 'cause.successAssoc': []}
	for i in range(minEpisode, maxEpisode + 1):
		# dfE = df[(df['episode'] == i) & (df['wlan.fc.type_subtype'] == 12) & (df['wlan.da'] == client)]
		# deauthCount = len(dfE)
		#
		# dfE2 = df[(df['episode'] == i) & ((df['wlan.fc.type_subtype'] == 1) | (df['wlan.fc.type_subtype'] == 3)) & (
		#       df['wlan_mgt.fixed.status_code'] == 0) & (df['wlan.da'] == client)]
		# successAssocCount = len(dfE2)
		#
		# cause = 'False'
		# if (deauthCount == 0 and successAssocCount > 0):
		#   cause = 'True'

		# output['successAssoc.deauth.count'].append(deauthCount)
		# output['success.assoc.count'].append(successAssocCount)
		output['success.assoc.count'].append(0)
		# output['cause.successAssoc'].append(cause)
		output['cause.successAssoc'].append('False')
	return output


class3FramesList = [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 26, 24, 25, 13, 14]


def class3Frames(df, minEpisode, maxEpisode):
	# print('Class 3 Frames...')
	output = {'class3frames.count': [], 'cause.class3': []}
	for i in range(minEpisode, maxEpisode + 1):
		dfE = df[(df['episode'] == i) & (df['wlan.fc.type_subtype'].isin(class3FramesList))]
		metric = len(dfE)

		cause = 'False'
		if metric > 0:
			cause = 'True'

		output['class3frames.count'].append(metric)
		output['cause.class3'].append(cause)
	return output


'''
consider only a single client
associate each packet captured with an episodeID (starting from 1, incremental)
so a pcap with {bla,bla,bla,preq1(0.5),preq2(0.6),bla,bla,preq3(1.7),preq4(2.8),bla,bla} becomes
1: {bla,bla,preq1,preq2}
2: {bla,bla,preq3}
3: {preq4}
aggregates window + following episode
'''


def defineEpisodes(df):
	dfX = df[(df['wlan.fc.type_subtype'] == 4)]
	dfX = dfX.iloc[::-1]
	lastPReqEpoch = 0
	pReqEpisodeStartIndex = []

	for index, row in dfX.iterrows():
		currentPReqEpoch = float(row['frame.time_epoch'])
		if abs(lastPReqEpoch - currentPReqEpoch) > 1:
			pReqEpisodeStartIndex.append(currentPReqEpoch)
		lastPReqEpoch = currentPReqEpoch

	pReqEpisodeStartIndex.sort()
	lastIndex = 0
	episode = 0

	for i in pReqEpisodeStartIndex:
		df.ix[(df['frame.time_epoch'] <= i) & (df['frame.time_epoch'] > lastIndex), 'episode'] = episode
		episode += 1
		lastIndex = i

	# df.ix[(df.index <= vLastIndex) & (df.index > lastIndex), 'episode'] = episode
	# not essentially part of any episode ^
	df = df[(df['episode'] > -1)]
	return df


def filterData(df, client):
	df = df[(df['wlan.ra'] == client) | (df['wlan.ta'] == client) | (df['wlan.sa'] == client) | (
			df['wlan.da'] == client) | (df['wlan.fc.type_subtype'] == 8)]
	return df


# #############################################################################

# get current directory
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
# raw csv directory
RAW_CSV_DIR = os.path.join(PROJECT_DIR, 'raw_csv_files')
# analyzed csv directory
ANALYZED_CSV_DIR = os.path.join(PROJECT_DIR, 'analyzed_csv_files')

# Supported Extensions - only files with supported extensions shall be read
SUPPORTED_EXTS = ['.csv', ]

# create directories if don't exist
if not os.path.exists(RAW_CSV_DIR) or not os.path.isdir(RAW_CSV_DIR):
	os.mkdir(RAW_CSV_DIR)
if not os.path.exists(ANALYZED_CSV_DIR) or not os.path.isdir(ANALYZED_CSV_DIR):
	os.mkdir(ANALYZED_CSV_DIR)

# make sure ANALYZED_CSV_DIR is empty
if len(os.listdir(ANALYZED_CSV_DIR)) != 0:
	print(ANALYZED_CSV_DIR, 'is not empty! Please empty the directory and try again.')
	exit(0)

# read all raw csv files
raw_csv_files = list()
for file in os.listdir(RAW_CSV_DIR):
	if os.path.splitext(file)[1] in SUPPORTED_EXTS:
		raw_csv_files.append(file)

# sort by name
raw_csv_files.sort()

# --------  SETUP  ---------
csv_delimiter = ','
# client = '18:34:51:35:e6:a3'
# client = '84:3a:4b:d9:35:54'
# client = '44:6d:57:31:40:6f'
client = 'c0:ee:fb:30:d7:17'

for idx, file in enumerate(raw_csv_files):

	# filter raw csv file
	raw_file = os.path.join(RAW_CSV_DIR, file)
	print(raw_file)

	df = pandas.read_csv(raw_file, sep = csv_delimiter, header = 0, index_col = False)
	df = filterData(df, client)
	df = defineEpisodes(df)
	# df.to_csv('csv/'+initfile+'_modif.csv', sep=',')

	# save filtered csv here if required!

	minE = int((df.head(1))['episode'])
	maxE = int((df.tail(1))['episode'])

	# apply proper tags
	tag1 = low_rssi(df, minE, maxE, client)
	tag2 = dataFrameLosses(df, minE, maxE, client)
	tag3 = powerStateLowToHigh(df, minE, maxE, client)
	tag4 = powerStateLowToHighV2(df, minE, maxE, client)
	tag5 = apDeauth(df, minE, maxE, client)
	tag6 = clientDeauth(df, minE, maxE, client)
	tag7 = beaconLoss(df, minE, maxE, client)
	tag8 = unsuccessAssocBlah(df, minE, maxE, client)
	tag9 = successAssocBlah(df, minE, maxE, client)
	tag10 = class3Frames(df, minE, maxE)
	finalResult = merge_dicts(tag1, tag2, tag3, tag4, tag5, tag6, tag7, tag8, tag9, tag10)

	finalResult['cause'] = ['' for x in range(len(finalResult['cause.apsideproc']))]

	drops = []
	for key, value in finalResult.items():
		if 'cause.' in key:
			for i in range(0, len(value)):
				if 'True' in value[i]:
					if finalResult['cause'][i] is None:
						finalResult['cause'][i] = get_tag_for_cause(key)
					else:
						finalResult['cause'][i] += get_tag_for_cause(key)
				else:
					finalResult['cause'][i] += ''
			drops.append(key)

	outputDF = pandas.DataFrame(finalResult)

	for i in drops:
		outputDF = outputDF.drop(i, axis = 1)

	# store final output
	output_csvname = os.path.basename(file)
	output_csvfile = os.path.join(ANALYZED_CSV_DIR, output_csvname)
	outputDF.to_csv(output_csvfile, sep = ',')


if __name__ == '__main__':
	main()
