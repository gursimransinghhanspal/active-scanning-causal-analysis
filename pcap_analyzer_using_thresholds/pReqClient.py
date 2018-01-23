# '''
# prints out all possible (not specifically) client MACs
# and corresponding number of pReqs
# from a give pcap
# '''
#
# import pandas
# import numpy as np
#
# def countPReqs(df, client):
# 	df = df[(df['wlan.fc.type_subtype'] == 4) & ((df['wlan.sa'] == client) | (df['wlan.da'] == client) | (df['wlan.ta'] == client))]
# 	return len(df)
#
#
# initfile = 'Experiment1_Acer_ath9k'
# csv_delimiter = ','
#
# filename = 'csv/'+initfile+'.csv'
# df = pandas.read_csv(filename, sep=csv_delimiter)
#
# allMacs = df['wlan.ra'].unique()
# np.concatenate((allMacs, df['wlan.sa'].unique(), df['wlan.ta'].unique(), df['wlan.da'].unique()))
#
# apMacs = df['wlan.bssid'].unique()
# apMacs.tolist()
#
# allMacs = np.unique(allMacs)
# allMacs = allMacs.tolist()
#
# for i in allMacs:
# 	if i in apMacs:
# 		allMacs.remove(i)
#
# for i in allMacs:
# 	macPreqCount = countPReqs(df, i)
# 	if macPreqCount > 0:
# 		print str(i) + '\t ' + str(macPreqCount)