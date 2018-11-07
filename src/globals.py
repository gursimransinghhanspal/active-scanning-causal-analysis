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
ProjectDirectory["data.record"] = os.path.join(ProjectDirectory["data"], 'record')
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
##
ProjectDirectory["logs"] = os.path.join(os.path.dirname(_current_dirpath), 'logs')


# *****************************************************************************
# *****************************************************************************

# NOTE: only use with Python >= 3.4, since maintaining enum ordering is very important here
# IMP: Do not change the ordering if you do not know what you are doing!
class FrameFields(enum.Enum):
    """ The fields to select from the cap file for the csv file. """

    frame_timeEpoch = 'frame.time_epoch'
    # frame_number = 'frame.number'
    # frame_len = 'frame.len'
    # radiotap_channel_freq = 'radiotap.channel.freq'
    # radiotap_mactime = 'radiotap.mactime'
    # radiotap_datarate = 'radiotap.datarate'
    radiotap_dbmAntsignal = 'radiotap.dbm_antsignal'
    data_len = 'data.len'
    # wlan_ds_currentChannel = 'wlan.ds.current_channel'
    # wlan_qbss_scount = 'wlan.qbss.scount'
    # wlan_duration = 'wlan.duration'
    # wlan_seq = 'wlan.seq'
    # wlan_qos_priority = 'wlan.qos.priority'
    # wlan_qos_amsdupresent = 'wlan.qos.amsdupresent'
    wlan_addr = 'wlan.addr'
    wlan_da = 'wlan.da'
    wlan_ra = 'wlan.ra'
    wlan_sa = 'wlan.sa'
    wlan_ta = 'wlan.ta'
    # wlan_ssid = 'wlan.ssid'
    wlan_bssid = 'wlan.bssid'
    # wlan_fc_ds = 'wlan.fc.ds'
    # wlan_fc_moredata = 'wlan.fc.moredata'
    # wlan_fc_frag = 'wlan.fc.frag'
    wlan_fc_pwrmgt = 'wlan.fc.pwrmgt'
    wlan_fc_retry = 'wlan.fc.retry'
    wlan_fc_type = 'wlan.fc.type'
    wlan_fc_typeSubtype = 'wlan.fc.type_subtype'
    # wlan_fixed_reasonCode = 'wlan.fixed.reason_code'
    wlan_fixed_statusCode = 'wlan.fixed.status_code'

    @property
    def v(self):
        return self.value

    pass


# *****************************************************************************
# *****************************************************************************


# Tags for Rule Based System Active Scanning Causes
class RbsTags(enum.Enum):
    ap_side_procedure = 'g'
    beacon_loss = 'h'
    class_3_frames = 'b'
    client_deauth = 'm'
    data_frame_loss = 'i'
    low_rssi = 'd'
    power_state = 'e'
    power_state_v2 = 'f'
    successful_association = 'c'
    unsuccessful_association = 'a'

    @property
    def v(self):
        return self.value

    pass


# *****************************************************************************
# *****************************************************************************


# ***** Active Scanning Causes *****
# Labels for ML flow
class ASCause(enum.Enum):
    apsp = 'apSideProcedures'
    bl = 'beaconLoss'
    ce = 'connectionEstablishment'
    lrssi = 'lowRSSI'
    pscanA = 'associatedPeriodicScan'
    pscanU = 'unassociatedPeriodicScan'
    pwr = 'powerState_lowToHigh'

    @property
    def v(self):
        return self.value

    @classmethod
    def asList(cls):
        as_causes = list()
        for cause in ASCause:
            as_causes.append(cause)
        return as_causes

    @classmethod
    def asSet(cls):
        return set(ASCause.asList())

    pass


# ***** Feature Transformation *****
# The metrics computed using the window and episode frames
# Superset of Features for ML flow
class Features(enum.Enum):
    #
    # compute using isolated window and episodes
    #
    rssi__mean = 'rssi.mean'
    rssi__stddev = 'rssi.stddev'
    rssi__linslope = 'rssi.linslope'
    non_empty_data_frames__count = 'nonEmptyDataFrames.count'
    non_empty_data_frames__rate = 'nonEmptyDataFrames.rate'
    sleep_frames__count = 'sleepFrames.count'
    sleep_frames__binary = 'sleepFrames.binary'
    empty_null_frames__count = 'emptyNullFrames.count'
    empty_null_frames__rate = 'emptyNullFrames.rate'
    directed_probe_requests__count = 'directedProbeRequests.count'
    directed_probe_requests__binary = 'directedProbeRequests.binary'
    broadcasted_probe_requests__count = 'broadcastedProbeRequests.count'
    broadcasted_probe_requests__binary = 'broadcastedProbeRequests.binary'
    beacon_loss__count = 'beaconLoss.count'
    awake_null_frames__count = 'awakeNullFrames.count'
    awake_null_frames__rate = 'awakeNullFrames.rate'
    sleep_null_frames__count = 'sleepNullFrames.count'
    sleep_null_frames__rate = 'sleepNullFrames.rate'
    ap_disconnection_frames__count = 'apDisconnectionFrames.count'
    ap_disconnection_frames__binary = 'apDisconnectionFrames.binary'
    client_disconnection_frames__count = 'clientDisconnectionFrames.count'
    client_disconnection_frames__binary = 'clientDisconnectionFrames.binary'
    client_associated__binary = 'clientAssociated.binary'
    client_associated__ternary = 'clientAssociated.ternary'
    #
    success_association_response__count = 'successAssociationResponse.count'
    unsuccess_association_response__count = 'unsuccessAssociationResponse.count'
    class3_frames__count = 'class3Frames.count'
    client_frames__rate = 'clientFrames.rate'
    ap_deauth__count = 'apDeauth.count'
    ack__count = 'ack.count'
    retry__ratio = 'retry.ratio'
    client_deauth__count = 'clientDeauth.count'

    #
    # requires use of multiple windows and episodes
    #
    client_connection_request_frames__count_1 = 'clientConnectionRequestFrames.count.1'
    client_connection_request_frames__binary_1 = 'clientConnectionRequestFrames.binary.1'
    client_connection_response_frames__count_1 = 'clientConnectionResponseFrames.count.1'
    client_connection_response_frames__binary_1 = 'clientConnectionResponseFrames.binary.1'
    client_connection_success_response_frames__count_1 = 'clientConnectionSuccessResponseFrames.count.1'
    client_connection_success_response_frames__binary_1 = 'clientConnectionSuccessResponseFrames.binary.1'

    client_connection_request_frames__count_3 = 'clientConnectionRequestFrames.count.3'
    client_connection_request_frames__binary_3 = 'clientConnectionRequestFrames.binary.3'
    client_connection_response_frames__count_3 = 'clientConnectionResponseFrames.count.3'
    client_connection_response_frames__binary_3 = 'clientConnectionResponseFrames.binary.3'
    client_connection_success_response_frames__count_3 = 'clientConnectionSuccessResponseFrames.count.3'
    client_connection_success_response_frames__binary_3 = 'clientConnectionSuccessResponseFrames.binary.3'

    client_connection_request_frames__count_5 = 'clientConnectionRequestFrames.count.5'
    client_connection_request_frames__binary_5 = 'clientConnectionRequestFrames.binary.5'
    client_connection_response_frames__count_5 = 'clientConnectionResponseFrames.count.5'
    client_connection_response_frames__binary_5 = 'clientConnectionResponseFrames.binary.5'
    client_connection_success_response_frames__count_5 = 'clientConnectionSuccessResponseFrames.count.5'
    client_connection_success_response_frames__binary_5 = 'clientConnectionSuccessResponseFrames.binary.5'

    # def f__client_connection_request_frames__count():
    #     # association req or reassociation req frames from the client
    #     connection_df = _from_client_df[
    #         (
    #             (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.association_request.v) |
    #             (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.reassociation_request.v)
    #         )
    #     ].copy()
    #     return int(connection_df.shape[0])
    #
    # def f__client_connection_request_frames__binary():
    #     return int(f__client_connection_request_frames__count() > 0)
    #
    # def f__client_connection_response_frames__count():
    #     # association req or reassociation req frames from the client
    #     connection_df = _to_client_df[
    #         (
    #             (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.association_response.v) |
    #             (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.reassociation_response.v)
    #         )
    #     ].copy()
    #     return int(connection_df.shape[0])
    #
    # def f__client_connection_response_frames__binary():
    #     return int(f__client_connection_response_frames__count() > 0)

    @property
    def v(self):
        return self.value

    @classmethod
    def asList(cls):
        wm = list()
        for metric in Features:
            wm.append(metric)
        return wm

    @classmethod
    def valuesAsList(cls):
        wm = list()
        for metric in Features:
            wm.append(metric.value)
        return wm

    pass


# ***** Extra fields to facilitate mapping back to the csv file *****
class RecordProperties(enum.Enum):
    relevant_client__mac = 'relevantClient.mac'
    episode__id = 'episode.id'
    episode_start__epoch = 'episodeStart.timeEpoch'
    episode_end__epoch = 'episodeEnd.timeEpoch'
    episode_duration__seconds = 'episodeDuration.seconds'
    episode_frames__count = 'episodeFrames.count'
    window__id = 'window.id'
    window_start__epoch = 'windowStart.timeEpoch'
    window_end__epoch = 'windowEnd.timeEpoch'
    window_duration__seconds = 'windowDuration.seconds'
    window_frames__count = 'windowFrames.count'
    #
    csv_file__name = 'csvFile.name'
    csv_file__relpath = 'csvFile.relpath'

    @property
    def v(self):
        return self.value

    @classmethod
    def asList(cls):
        wm = list()
        for metric in RecordProperties:
            wm.append(metric)
        return wm

    @classmethod
    def valuesAsList(cls):
        wm = list()
        for metric in RecordProperties:
            wm.append(metric.value)
        return wm

    pass


# *****************************************************************************
# *****************************************************************************


# ***** Rule Based System Metrics *****
# RBSMetrics = {
#     Features.rssi__mean,
#     Features.rssi__stddev,
#     Features.frames__loss_ratio,
#     Features.frames__arrival_rate,
#     Features.ap_deauth_frames__count,
#     Features.client_deauth_frames__count,
#     Features.beacons__count,
#     Features.max_consecutive_beacon_loss__count,
#     Features.ack__count,
#     Features.null_frames__count,
#     Features.failure_assoc__count,
#     Features.success_assoc__count,
#     Features.class_3_frames__count,
# }

# ***** Feature Selection *****
# These are all the features considered for ML flow with 7 binary models
MLFeaturesForCause = {
    ASCause.apsp  : [
        Features.ap_disconnection_frames__binary,
    ],
    ASCause.bl    : [
        Features.directed_probe_requests__binary,
        # Features.beacon_loss__count,
        Features.awake_null_frames__rate,
    ],
    ASCause.ce    : [
        Features.client_connection_request_frames__binary_3,
        Features.client_connection_response_frames__binary_3,
        Features.client_connection_success_response_frames__binary_3,
    ],
    ASCause.lrssi : [
        Features.rssi__mean,
        Features.rssi__stddev,
        Features.rssi__linslope,
    ],
    ASCause.pscanA: [
        Features.non_empty_data_frames__rate,
        Features.sleep_frames__binary,
    ],
    ASCause.pscanU: [
        Features.client_associated__binary,
    ],
    ASCause.pwr   : [
        Features.empty_null_frames__rate,
    ]
}

# A list of all ML Features
# def mlFeaturesAsList():
#     features = list()
#     for key in MLFeaturesForCause.keys():
#         features.extend(MLFeaturesForCause[key])
#     return features


# *****************************************************************************
# *****************************************************************************

cap_extensions = ['.cap', '.pcap', '.pcapng', ]
csv_extensions = ['.csv', ]

# *****************************************************************************
# *****************************************************************************

if __name__ == '__main__':
    pass
