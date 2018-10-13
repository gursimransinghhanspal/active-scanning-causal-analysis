#!python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# |- globals.py
#       := Holds data that is required and is common across all modules


import enum
import os

# *****************************************************************************
# *****************************************************************************

# Path to directory containing the "globals.py" file. All other paths are defined relative to this file
_current_dirpath = os.path.dirname(os.path.abspath(__file__))

ProjectDirectory = dict()
#
ProjectDirectory["src"] = _current_dirpath
##
ProjectDirectory["data"] = os.path.join(os.path.dirname(_current_dirpath), 'data')
###
ProjectDirectory["data.cap"] = os.path.join(ProjectDirectory["data"], 'cap')
###
ProjectDirectory["data.csv"] = os.path.join(ProjectDirectory["data"], 'csv')
###
ProjectDirectory["data.records"] = os.path.join(ProjectDirectory["data"], 'records')
###
ProjectDirectory["data.records_merged"] = os.path.join(ProjectDirectory["data"], 'records_merged')
###
ProjectDirectory["data.ml"] = os.path.join(ProjectDirectory["data"], 'ml')
###
ProjectDirectory["data.ml_labeled"] = os.path.join(ProjectDirectory["data"], 'ml_labeled')
###
ProjectDirectory["data.ml_unlabeled"] = os.path.join(ProjectDirectory["data"], 'ml_unlabeled')
##
ProjectDirectory["models"] = os.path.join(os.path.dirname(_current_dirpath), 'models')


# *****************************************************************************
# *****************************************************************************

# NOTE: only use with Python >= 3.4, since maintaining enum ordering is very important here
# IMP: Do not change the ordering if you do not know what you are doing!
class FrameFields(enum.Enum) :
    """ The fields to select from the cap file for the csv file. """

    frame_timeEpoch = 'frame.time_epoch'
    radiotap_datarate = 'radiotap.datarate'
    radiotap_dbmAntsignal = 'radiotap.dbm_antsignal'
    data_len = 'data.len'
    wlan_addr = 'wlan.addr'
    wlan_da = 'wlan.da'
    wlan_ra = 'wlan.ra'
    wlan_sa = 'wlan.sa'
    wlan_ta = 'wlan.ta'
    wlan_ssid = 'wlan.ssid'
    wlan_bssid = 'wlan.bssid'
    wlan_fc_pwrmgt = 'wlan.fc.pwrmgt'
    wlan_fc_retry = 'wlan.fc.retry'
    wlan_fc_type = 'wlan.fc.type'
    wlan_fc_typeSubtype = 'wlan.fc.type_subtype'
    wlan_fixed_statusCode = 'wlan.fixed.status_code'  # required only for assigning rbs tags
    pass


# *****************************************************************************
# *****************************************************************************


# Tags for Rule Based System Active Scanning Causes
# class RBSCauses(enum.Enum):
#     ap_side_procedure = 'g'
#     beacon_loss = 'h'
#     class_3_frames = 'b'
#     client_deauth = 'm'
#     data_frame_loss = 'i'
#     low_rssi = 'd'
#     power_state = 'e'
#     power_state_v2 = 'f'
#     successful_association = 'c'
#     unsuccessful_association = 'a'
#     pass


# *****************************************************************************
# *****************************************************************************


# ***** Active Scanning Causes *****
# Labels for ML flow
class ASCause(enum.Enum) :
    apsp = 'apSideProcedures'
    bl = 'beaconLoss'
    ce = 'connectionEstablishment'
    lrssi = 'lowRSSI'
    pscanA = 'associatedPeriodicScan'
    pscanU = 'unassociatedPeriodicScan'
    pwr = 'powerState_lowToHigh'

    @classmethod
    def asList(cls) :
        as_causes = list()
        for cause in ASCause :
            as_causes.append(cause)
        return as_causes

    @classmethod
    def asSet(cls) :
        return set(ASCause.asList())

    pass


# ***** Feature Transformation *****
# The metrics computed using the window and episode frames
# Superset of Features for ML flow
class WindowMetrics(enum.Enum) :
    # ML features
    rssi__mean = 'rssi.mean'
    rssi__stddev = 'rssi.stddev'
    rssi__linslope = 'rssi.linslope'
    non_empty_data_frames__rate = 'nonEmptyDataFrame.rate'
    sleep_frames__binary = 'sleepFrames.binary'
    empty_null_frames__rate = 'emptyNullFrames.rate'
    associated_probe_requests__binary = 'associatedProbeRequests.binary'
    max_consecutive_beacon_loss__count = 'maxConsecutiveBeaconLoss.count'
    awake_null_frames__rate = 'awakeNullFrames.rate'
    ap_disconnection_frames__binary = 'apDisconnectionFrames.binary'
    client_connection_frame__binary = 'clientConnectionFrames.binary'
    client_associated__binary = 'clientAssociated.binary'

    @classmethod
    def asList(cls) :
        wm = list()
        for metric in WindowMetrics :
            wm.append(metric)
        return wm

    pass


# ***** Extra fields to facilitate mapping back to the csv file *****
class RecordProperties(enum.Enum):
    csv_file__uuid = 'csvFile.uuid'
    window__id = 'window.id'
    window_start__epoch = 'windowStart.timeEpoch'
    window_end__epoch = 'windowEnd.timeEpoch'
    window_duration__seconds = 'windowDuration.seconds'
    relevant_client__mac = 'relevantClient.mac'
    episode__id = 'episode.id'
    episode_start__epoch = 'episodeStart.timeEpoch'
    episode_end__epoch = 'episodeEnd.timeEpoch'
    episode_duration__seconds = 'episodeDuration.seconds'
    pass


# ***** Mapping file fields *****
# class RecordToCsvMappingFields(enum.Enum):
#     timestamp__date = 'timestamp.date'
#     timestamp__time = 'timestamp.time'
#     csv_file__name = 'csvFile.name'
#     csv_file__uuid = 'csvFile.uuid'


# *****************************************************************************
# *****************************************************************************


# ***** Rule Based System Metrics *****
# RBSMetrics = {
#     WindowMetrics.rssi__mean,
#     WindowMetrics.rssi__sd,
#     WindowMetrics.frames__loss_ratio,
#     WindowMetrics.frames__arrival_rate,
#     WindowMetrics.ap_deauth_frames__count,
#     WindowMetrics.client_deauth_frames__count,
#     WindowMetrics.beacons__count,
#     WindowMetrics.max_consecutive_beacon_loss__count,
#     WindowMetrics.ack__count,
#     WindowMetrics.null_frames__count,
#     WindowMetrics.failure_assoc__count,
#     WindowMetrics.success_assoc__count,
#     WindowMetrics.class_3_frames__count,
# }

# ***** Feature Selection *****
# These are all the features considered for ML flow with 7 binary models
MLFeaturesForCause = {
    ASCause.apsp   : [
        WindowMetrics.ap_disconnection_frames__binary,
    ],
    ASCause.bl     : [
        WindowMetrics.associated_probe_requests__binary,
        WindowMetrics.max_consecutive_beacon_loss__count,
        WindowMetrics.awake_null_frames__rate,
    ],
    ASCause.ce     : [
        WindowMetrics.client_connection_frame__binary,
    ],
    ASCause.lrssi  : [
        WindowMetrics.rssi__mean,
    ],
    ASCause.pscanA : [
        WindowMetrics.non_empty_data_frames__rate,
        WindowMetrics.sleep_frames__binary,
    ],
    ASCause.pscanU : [
        WindowMetrics.client_associated__binary,
    ],
    ASCause.pwr    : [
        WindowMetrics.empty_null_frames__rate,
    ]
}


# A list of all ML Features
def mlFeaturesAsList() :
    features = list()
    for key in MLFeaturesForCause.keys() :
        features.extend(MLFeaturesForCause[key])
    return features


# *****************************************************************************
# *****************************************************************************

cap_extensions = ['.cap', '.pcap', '.pcapng', ]
csv_extensions = ['.csv', ]

# *****************************************************************************
# *****************************************************************************

if __name__ == '__main__' :
    pass
