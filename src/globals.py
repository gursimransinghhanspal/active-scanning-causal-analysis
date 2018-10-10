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


class FrameSubtypes(enum.Enum):
    # type 0 (management)
    association_request = 0x00
    association_response = 0x01
    reassociation_request = 0x02
    reassociation_response = 0x03
    probe_request = 0x04
    probe_response = 0x05
    beacon = 0x08
    atim = 0x09
    disassociation = 0x0a
    authentication = 0x0b
    deauthentication = 0x0c
    action = 0x0d

    # type 1 (control)
    block_ack_request = 0x18
    block_ack = 0x19
    ps_poll = 0x1a
    rts = 0x1b
    cts = 0x1c
    ack = 0x1d
    cf_end = 0x1e
    cf_end_cf_ack = 0x1f

    # type 2 (data)
    data = 0x20
    data_cf_ack = 0x21
    data_cf_poll = 0x22
    data_cf_ack_cf_poll = 0x23
    null = 0x24
    cf_ack = 0x25
    cf_poll = 0x26
    cf_ack_cf_poll = 0x27
    qos_data = 0x28
    qos_data_cf_ack = 0x29
    qos_data_cf_poll = 0x2a
    qos_data_cf_ack_cf_poll = 0x2b
    qos_null = 0x2c
    qos_cf_poll = 0x2e
    qos_cf_ack = 0x2f
    pass


# *****************************************************************************

# NOTE: only use with Python >= 3.4, since maintaining enum ordering is very important here
# IMP: Do not change the ordering if you do not know what you are doing!
class FrameFields(enum.Enum):
    """ The fields to select from the cap file for the csv file """

    frame_timeEpoch = 'frame.time_epoch'
    wlan_bssid = 'wlan.bssid'
    wlan_sa = 'wlan.sa'
    wlan_da = 'wlan.da'
    wlan_ta = 'wlan.ta'
    wlan_ra = 'wlan.ra'
    wlan_fixed_statusCode = 'wlan.fixed.status_code'  # required only for assigning rbs tags
    wlan_ssid = 'wlan.ssid'
    wlan_fc_typeSubtype = 'wlan.fc.type_subtype'
    wlan_fc_retry = 'wlan.fc.retry'
    wlan_fc_pwrmgt = 'wlan.fc.pwrmgt'
    radiotap_datarate = 'radiotap.datarate'
    radiotap_dbmAntsignal = 'radiotap.dbm_antsignal'
    pass


# *****************************************************************************

# Tags for Rule Based System Active Scanning Causes
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
    pass


# *****************************************************************************
# the identified active scanning causes
class ASCause(enum.Enum):
    apsp = 'ap_side_procedures'
    bl = 'beacon_loss'
    ce = 'connection_establishment'
    # dfl = 'data_frame_loss'
    lrssi = 'low_rssi'
    pscanA = 'periodic_scan_associated'
    pscanU = 'periodic_scan_unassociated'
    # pwr = 'power_state_low_to_high'

    @classmethod
    def asList(cls):
        as_causes = list()
        for cause in ASCause:
            as_causes.append(cause)
        return as_causes

    @classmethod
    def asSet(cls):
        return set(ASCause.asList())


# All window metrics -- for ML and RBS flow merged!
class WindowMetrics(enum.Enum):
    class_3_frames__count = 'class_3_frames__count'
    class_3_frames__binary = 'class_3_frames__binary'

    client_associated__binary = 'client_associated__binary'

    frames__arrival_rate = 'frames__arrival_rate'

    pspoll__count = 'pspoll__count'
    pspoll__binary = 'pspoll__binary'

    pwrmgt_cycle__count = 'pwrmgt_cycle__count'
    pwrmgt_cycle__binary = 'pwrmgt_cycle__binary'

    rssi__slope = 'rssi__slope'

    ap_deauth_frames__count = 'ap_deauth_frames__count'
    ap_deauth_frames__binary = 'ap_deauth_frames__binary'

    max_consecutive_beacon_loss__count = 'max_consecutive_beacon_loss__count'
    max_consecutive_beacon_loss__binary = 'max_consecutive_beacon_loss__binary'

    beacons_linear_slope__difference = 'beacons_linear_slope__difference'

    null_frames__ratio = 'null_frames__ratio'

    connection_frames__count = 'connection_frames__count'
    connection_frames__binary = 'connection_frames__binary'

    frames__loss_ratio = 'frames__loss_ratio'
    ack_to_data__ratio = 'ack_to_data__ratio'
    datarate__slope = 'datarate__slope'

    rssi__mean = 'rssi__mean'
    rssi__sd = 'rssi__sd'
    client_deauth_frames__count = 'client_deauth_frames__count'
    beacons__count = 'beacons__count'
    ack__count = 'ack__count'
    null_frames__count = 'null_frames__count'
    failure_assoc__count = 'failure_assoc__count'
    success_assoc__count = 'success_assoc__count'

    @classmethod
    def asList(cls):
        wm = list()
        for metric in WindowMetrics:
            wm.append(metric)
        return wm

    pass


# *****************************************************************************

class WindowProperties(enum.Enum):
    frames_file__uuid = 'frames_file__uuid'
    window__id = 'window__id'
    window_start__time_epoch = 'window_start__time_epoch'
    window_end__time_epoch = 'window_end__time_epoch'
    window_duration__seconds = 'window_duration__seconds'
    associated_client__mac = 'associated_client__mac'
    pass


class EpisodeProperties(enum.Enum):
    episode__id = 'episode__id'
    episode_start__time_epoch = 'episode_start__time_epoch'
    episode_end__time_epoch = 'episode_end__time_epoch'
    episode_duration__seconds = 'episode_duration__seconds'
    pass


class WindowToFrameMappingParameters(enum.Enum):
    timestamp__date = 'timestamp__date'
    timestamp__time = 'timestamp__time'
    frames_file__name = 'frames_file__name'
    frames_file__uuid = 'frames_file__uuid'


RBSFeatures = {
    WindowMetrics.rssi__mean,
    WindowMetrics.rssi__sd,
    WindowMetrics.frames__loss_ratio,
    WindowMetrics.frames__arrival_rate,
    WindowMetrics.ap_deauth_frames__count,
    WindowMetrics.client_deauth_frames__count,
    WindowMetrics.beacons__count,
    WindowMetrics.max_consecutive_beacon_loss__count,
    WindowMetrics.ack__count,
    WindowMetrics.null_frames__count,
    WindowMetrics.failure_assoc__count,
    WindowMetrics.success_assoc__count,
    WindowMetrics.class_3_frames__count,
}

# These are all the features considered for ML flow
# These are selected using feature selection algorithms
FeaturesForCause = {
    ASCause.apsp: [WindowMetrics.ap_deauth_frames__count, ],
    ASCause.bl: [WindowMetrics.beacons_linear_slope__difference,
                 WindowMetrics.max_consecutive_beacon_loss__count, ],
    ASCause.ce: [WindowMetrics.connection_frames__count, ],
    ASCause.lrssi: [WindowMetrics.rssi__mean,
                    WindowMetrics.rssi__slope, ],
    ASCause.pscanA: [WindowMetrics.frames__arrival_rate,
                     WindowMetrics.pspoll__count,
                     WindowMetrics.pwrmgt_cycle__count, ],
    ASCause.pscanU: [WindowMetrics.class_3_frames__count,
                     WindowMetrics.client_associated__binary],
    # ASCause.pwr: [WindowMetrics.frames__arrival_rate,
    #               WindowMetrics.null_frames__ratio,
    #               WindowMetrics.pspoll__count, ],
}

#
MLFeatures = [
    WindowMetrics.ap_deauth_frames__count,
    WindowMetrics.beacons_linear_slope__difference,
    WindowMetrics.max_consecutive_beacon_loss__count,
    WindowMetrics.connection_frames__count,
    WindowMetrics.rssi__mean,
    WindowMetrics.rssi__slope,
    WindowMetrics.frames__arrival_rate,
    WindowMetrics.pspoll__count,
    WindowMetrics.pwrmgt_cycle__count,
    WindowMetrics.class_3_frames__count,
    WindowMetrics.client_associated__binary,
    WindowMetrics.frames__arrival_rate,
    WindowMetrics.null_frames__ratio,
]

# ### Other ###
class_3_frames_subtypes = [
    FrameSubtypes.data.value,
    FrameSubtypes.data_cf_ack.value,
    FrameSubtypes.data_cf_poll.value,
    FrameSubtypes.data_cf_ack_cf_poll.value,
    FrameSubtypes.null.value,
    FrameSubtypes.cf_ack.value,
    FrameSubtypes.cf_poll.value,
    FrameSubtypes.cf_ack_cf_poll.value,
    FrameSubtypes.qos_data.value,
    FrameSubtypes.qos_data_cf_ack.value,
    FrameSubtypes.qos_data_cf_poll.value,
    FrameSubtypes.qos_data_cf_ack_cf_poll.value,
    FrameSubtypes.qos_null.value,
    FrameSubtypes.qos_cf_poll.value,
    FrameSubtypes.qos_cf_ack.value,
    FrameSubtypes.ps_poll.value,
    FrameSubtypes.block_ack_request.value,
    FrameSubtypes.block_ack.value,
    FrameSubtypes.action.value,
    14,  # type 0 (management), reserved
]

cap_extensions = ['.cap', '.pcap', '.pcapng', ]
csv_extensions = ['.csv', ]

if __name__ == '__main__':
    pass
