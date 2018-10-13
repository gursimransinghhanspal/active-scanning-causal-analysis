#!python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# Preprocessor
# |- csv2records.py
#       := Processes CSV files created by "cap2csv.py" to create records which can be used for machine learning
#
#
import datetime
import enum
import math
import sys
from os import path, walk

import numpy as np
import pandas as pd
from scipy.stats import linregress

from globals import (FrameFields, ProjectDirectory, RecordProperties, WindowMetrics, csv_extensions)
from src.aux import createDirectoryIfRequired, envSetup, selectFilesByExtension

__broadcast_bssid = 'ff:ff:ff:ff:ff:ff'


class FrameSubtypes(enum.Enum):
    # ** type 0 (management) **
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

    # ** type 1 (control) **
    block_ack_request = 0x18
    block_ack = 0x19
    ps_poll = 0x1a
    rts = 0x1b
    cts = 0x1c
    ack = 0x1d
    cf_end = 0x1e
    cf_end_cf_ack = 0x1f

    # ** type 2 (data) **
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

    # NOTE:
    # The below 3 methods have been defined using the information available in IEEE 802.11 standard v2012
    # refer pages 1012, 1013
    @classmethod
    def pdFilter_class1(cls, frame, sta_bssids):
        c1_subtypes = [
            # --- control
            cls.rts.value,
            cls.cts.value,
            cls.ack.value,
            cls.cf_end_cf_ack.value,
            cls.cf_end.value,
            cls.block_ack.value,  # assume IBSS
            cls.block_ack_request.value,  # assume IBSS
            # --- management
            cls.probe_request.value,
            cls.probe_response.value,
            cls.beacon.value,
            cls.authentication.value,
            cls.deauthentication.value,
            cls.atim.value,
            cls.action.value,  # assume same as "public action" frames
            # don't know "self-protected action" frames
            # don't know action and action no ack frames
        ]
        c1_data_types = [
            cls.data.value,
            cls.data_cf_ack.value,
            cls.data_cf_poll.value,
            cls.data_cf_ack_cf_poll.value,
            cls.null.value,
            cls.cf_ack.value,
            cls.cf_poll.value,
            cls.cf_ack_cf_poll.value,
            cls.qos_data.value,
            cls.qos_data_cf_ack.value,
            cls.qos_data_cf_poll.value,
            cls.qos_data_cf_ack_cf_poll.value,
            cls.qos_null.value,
            cls.qos_cf_poll.value,
            cls.qos_cf_ack.value,
        ]

        if frame[FrameFields.wlan_fc_typeSubtype.value] in c1_subtypes:
            return True
        #
        b1 = frame[FrameFields.wlan_fc_typeSubtype.value] in c1_data_types
        b2 = frame[FrameFields.wlan_sa.value] in sta_bssids or frame[FrameFields.wlan_ta.value] in sta_bssids
        b3 = frame[FrameFields.wlan_da.value] in sta_bssids or frame[FrameFields.wlan_ra.value] in sta_bssids
        if b1 and b2 and b3:
            return True
        #
        return False

    @classmethod
    def pdFilter_class2(cls, frame):
        c2_subtypes = [
            cls.association_request.value,
            cls.association_response.value,
            cls.reassociation_request.value,
            cls.reassociation_response.value,
            cls.disassociation.value,
        ]

        if frame[FrameFields.wlan_fc_typeSubtype.value] in c2_subtypes:
            return True
        #
        return False

    @classmethod
    def pdFilter_class3(cls, frame, sta_bssids):
        c3_subtypes = [
            cls.ps_poll.value,
        ]

        if frame[FrameFields.wlan_fc_typeSubtype.value] in c3_subtypes:
            return True
        #
        return not FrameSubtypes.pdFilter_class1(frame, sta_bssids) and not FrameSubtypes.pdFilter_class2(frame)


# *****************************************************************************
# *****************************************************************************

def pdFilter_wlanAddrContains(wlan_addr, the_addr, on_empty = False):
    if the_addr is None:
        return on_empty

    wlan_addrs = str(wlan_addr).lower().split(',')
    return str(the_addr).lower() in wlan_addrs


def pdFilter_wlanAddrContainsAny(wlan_addr, addr_set, on_empty = False, remove_broadcast = True):
    if addr_set is None or len(addr_set) == 0:
        return on_empty

    wlan_addrs = set(str(wlan_addr).lower().split(','))
    wlan_addrs = wlan_addrs.difference({None, })
    addr_set = addr_set.difference({None, })
    if remove_broadcast:
        wlan_addrs = wlan_addrs.difference({__broadcast_bssid, })
        addr_set = addr_set.difference({__broadcast_bssid, })

    for the_addr in addr_set:
        if str(the_addr).lower() in wlan_addrs:
            return True
    return False


def pdFilter_wlanAddrEquals(wlan_addr, addr_set, on_empty = False, remove_broadcast = True):
    if addr_set is None or len(addr_set) == 0:
        return on_empty

    wlan_addrs = set(str(wlan_addr).lower().split(','))
    wlan_addrs = wlan_addrs.difference({None, })
    addr_set = addr_set.difference({None, })
    if remove_broadcast:
        wlan_addrs = wlan_addrs.difference({__broadcast_bssid, })
        addr_set = addr_set.difference({__broadcast_bssid, })

    for the_addr in addr_set:
        if str(the_addr).lower() not in wlan_addrs:
            return False
    #
    if len(wlan_addrs) == len(addr_set):
        return True
    #
    return False


def dataframeFilter_framesFrom(dataframe, the_src):
    if dataframe is None or dataframe.shape[0] == 0:
        return None

    return dataframe[
        (
            dataframe[FrameFields.wlan_sa.value].apply(lambda sa: str(sa).lower() == str(the_src).lower(), 0) |
            dataframe[FrameFields.wlan_ta.value].apply(lambda ta: str(ta).lower() == str(the_src).lower(), 0)
        )
    ].copy()


def dataframeFilter_framesTowards(dataframe, the_dest):
    if dataframe is None or dataframe.shape[0] == 0:
        return None

    return dataframe[
        (
            dataframe[FrameFields.wlan_da.value].apply(lambda da: str(da).lower() == str(the_dest).lower(), 0) |
            dataframe[FrameFields.wlan_ra.value].apply(lambda ra: str(ra).lower() == str(the_dest).lower(), 0)
        )
    ].copy()


def dataframeFilter_relevantFrames(dataframe: pd.DataFrame, clients = None, access_points = None):
    """ Filter the frames that belong to only the relevant clients or relevant APs """

    if dataframe is None or dataframe.shape[0] == 0:
        return None

    return dataframe[
        (
            dataframe[FrameFields.wlan_addr.value].apply(lambda wa: pdFilter_wlanAddrContainsAny(wa, clients), 0) |
            dataframe[FrameFields.wlan_addr.value].apply(lambda wa: pdFilter_wlanAddrContainsAny(wa, access_points), 0)
        )
    ].copy()


def dataframeFilter_relevantFrames2(dataframe: pd.DataFrame, client, access_point = None):
    """ Filter the frames that belong to only the relevant clients or relevant APs """

    if dataframe is None or dataframe.shape[0] == 0:
        return None

    return dataframe[
        (
            dataframe[FrameFields.wlan_addr.value].apply(lambda wa: pdFilter_wlanAddrContains(wa, client), 0) |
            dataframe[FrameFields.wlan_addr.value].apply(lambda wa: pdFilter_wlanAddrEquals(wa, {access_point, }), 0) |
            dataframe[FrameFields.wlan_addr.value].apply(lambda wa: pdFilter_wlanAddrEquals(wa, {client, access_point, }), 0)
        )
    ].copy()


# *****************************************************************************
# *****************************************************************************

def allAccessPointsIn(dataframe):
    """
    Retrieve the BSSIDs of all Access Points that can be detected in the given data-frame...
    We use the `wlan.bssid` field associated with all the beacon (`wlan.fc.type_subtype` = 8) frames
    """

    if dataframe is None or dataframe.shape[0] == 0:
        return list()

    # filter out only the beacon frames
    beacon_df: pd.DataFrame = dataframe[
        (dataframe[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.beacon.value)
    ].copy()
    if beacon_df is None or beacon_df.shape[0] == 0:
        return list()
    #
    # put all non-null, unique BSSIDs in a list
    bssids_df = beacon_df[FrameFields.wlan_bssid.value].copy()
    bssids_df = bssids_df[bssids_df.notna()]
    bssids = bssids_df.apply(lambda a: str(a).lower(), 0).unique().tolist()
    # remove broadcast address
    if __broadcast_bssid in bssids:
        bssids.remove(__broadcast_bssid)
    return sorted(bssids)


def allClientsIn(dataframe):
    """
    Retrieve the MAC addresses of all client devices that can be detected in the given data-frame...
    Only devices who trigger episodes are regarded as clients, so we use probe requests
    """

    if dataframe is None or dataframe.shape[0] == 0:
        return list()

    # filter out only the probe request frames
    probe_request_df = dataframe[
        (dataframe[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.probe_request.value)
    ].copy()
    if probe_request_df is None or probe_request_df.shape[0] == 0:
        return list()
    #
    mac_addrs = set()
    sa_df = probe_request_df[FrameFields.wlan_sa.value].copy()
    sa_df = sa_df[sa_df.notna()]
    sa_df = sa_df.apply(lambda a: str(a).lower(), 0).unique()
    mac_addrs.update(sa_df.values)
    ta_df = probe_request_df[FrameFields.wlan_ta.value].copy()
    ta_df = ta_df[ta_df.notna()]
    ta_df = ta_df.apply(lambda a: str(a).lower(), 0).unique()
    mac_addrs.update(ta_df.values)
    # remove broadcast address
    mac_addrs = mac_addrs.difference({__broadcast_bssid, })
    return sorted(mac_addrs)


def isClientAssociatedWithAp(dataframe, the_client):
    if dataframe is None or dataframe.shape[0] == 0:
        return 0

    # all frames relevant to the client
    client_df = dataframe[
        (dataframe[FrameFields.wlan_addr.value].apply(lambda wa: pdFilter_wlanAddrContains(wa, the_client), 0))
    ].copy()
    if client_df is None or client_df.shape[0] == 0:
        return 0

    # filter out class3 frames
    class3_df = client_df[
        (client_df.apply(lambda frame: FrameSubtypes.pdFilter_class3(frame, allAccessPointsIn(dataframe)), 1))
    ].copy()
    return int(class3_df.shape[0] > 0)


def staAssociatedWithClient(dataframe, the_client):
    """
    :param dataframe: the dataframe to process
    :type dataframe: NDFrame
    :param the_client: client's MAC address
    :type the_client: str
    :return: the BSSID of the associated AP
    :rtype: Union[str, None]
    """

    if dataframe is None or dataframe.shape[0] == 0:
        return None

    if not isClientAssociatedWithAp(dataframe, the_client):
        return None

    from_client_df = dataframeFilter_framesFrom(dataframe, the_client)
    bssids_df = from_client_df[FrameFields.wlan_bssid.value].copy()
    bssids_df = bssids_df[bssids_df.notna()]
    bssids = bssids_df.apply(lambda a: str(a).lower(), 0).unique().tolist()
    #
    # remove broadcast address
    if __broadcast_bssid in bssids:
        bssids.remove(__broadcast_bssid)
    #
    if len(bssids) == 0:
        return None  # not associated with any AP
    elif len(bssids) == 1:
        return bssids[0]
    elif len(bssids) > 1:
        print("accessPointAssociatedWithClient: The associated AP for client `{:s}` cannot be determined uniquely.",
              len(bssids), "BSSIDs found.", file = sys.stderr)
        raise ValueError("Multiple BSSIDs associated to the client in the dataframe!")


# *****************************************************************************
# *****************************************************************************


def defineEpisodeAndWindowBoundaries(
    dataframe: pd.DataFrame, true_episode_epochs: np.array = None, true_epoch_delta_threshold = 10
):
    """
    Definition of an episode:
      for each client whose frames have been captured by the sniffer, we partition captured AS frames corresponding to
      the client into non-overlapping episodes of AS. Specifically, if a PReq from a client is separated from its
      previous PReq in the capture by more than a second, we treat this PReq as the start of a new episode of AS by the
      client.
      Ideally, the duration of an episode is expected to be less than 1 second

    Definition of a window:
      We derive metrics and simple rules to infer the cause of a given episode of AS. The metrics are calculated
      using a window of frames that precedes the AS episode. This window extends from the end of the previous episode
      to the start of the current episode.

    Bundle frames into episodes and windows by assigning a `window_index` field to each frame.
    Returns:
        1. dataframe with `window__id` and `episode__id` field
        2. count
        3. indexes
    """

    if dataframe is None or dataframe.shape[0] == 0:
        return None

    # add `window__id` and `episode__id` field to all the frames
    dataframe.loc[:, RecordProperties.window__id.value] = -1
    dataframe.loc[:, RecordProperties.episode__id.value] = -1

    # filter probe request frames
    probe_request_df = dataframe[
        (dataframe[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.probe_request.value)
    ].copy()
    print("\t\t\t", "••• Number of probe requests:", len(probe_request_df))
    # if no probe requests found return
    if probe_request_df is None or probe_request_df.shape[0] == 0:
        return None

    # sort the dataframe by `frame.timeEpoch`
    probe_request_df = probe_request_df.sort_values(
        by = FrameFields.frame_timeEpoch.value,
        axis = 0,
        ascending = True
    )

    # filter out true epochs before creating episodes
    if true_episode_epochs is not None:
        true_epoch_filter = np.zeros(probe_request_df.shape[0])
        for _idx, series in probe_request_df.iterrows():
            true_epoch_filter[_idx] = np.any(
                np.absolute(true_episode_epochs - float(series[FrameFields.frame_timeEpoch.value]))
                <= true_epoch_delta_threshold
            )
        probe_request_df = probe_request_df[true_epoch_filter]
        print("\t\t\t", "••• Number of probe requests (after true epoch filter):", len(probe_request_df))

    # assign episode ids to probe-requests
    current_episode_id = 1
    previous_epoch = float(probe_request_df[FrameFields.frame_timeEpoch.value].values[0])
    for _idx, series in probe_request_df.iterrows():
        current_epoch = float(series[FrameFields.frame_timeEpoch.value])
        if math.fabs(previous_epoch - current_epoch) >= 1:
            current_episode_id += 1
        # NOTE: assigning directly in the dataframe not the preq view
        dataframe.loc[_idx, RecordProperties.episode__id.value] = current_episode_id
        previous_epoch = current_epoch

    # some metrics regarding episodes
    episode_bounds = list()
    episode_durations = list()
    for _id in range(1, current_episode_id + 1):
        _v = dataframe[dataframe[RecordProperties.episode__id.value] == _id][FrameFields.frame_timeEpoch.value].values
        start = _v[0]
        end = _v[len(_v) - 1]
        episode_bounds.append((start, end))
        episode_durations.append(math.fabs(end - start))

    print("\t\t\t", "••• Number of episodes:", current_episode_id)
    print("\t\t\t", "••• Max episode duration:", np.max(episode_durations))
    print("\t\t\t", "••• Mean episode duration:", np.mean(episode_durations))
    print("\t\t\t", "••• Std. dev for episode duration:", np.std(episode_durations))

    # give sensible `window__id` and `episode__id` to respective frames
    # NOTE: `window__id` and `episode__id` start from 1 not 0.

    # for first episode
    episode_bounds.insert(0, (0.0, 0.0))

    for _idx in range(1, len(episode_bounds)):
        _previous_bound = episode_bounds[_idx - 1]
        _current_bound = episode_bounds[_idx]

        dataframe.loc[
            ((dataframe[FrameFields.frame_timeEpoch.value] > _previous_bound[1]) &
             (dataframe[FrameFields.frame_timeEpoch.value] < _current_bound[0])),
            RecordProperties.window__id.value
        ] = _idx

    # this removes frames that could not be assigned to any window or episode
    dataframe[RecordProperties.window__id.value] = dataframe[RecordProperties.window__id.value].astype(int)
    dataframe[RecordProperties.episode__id.value] = dataframe[RecordProperties.episode__id.value].astype(int)
    dataframe = dataframe[
        ((dataframe[RecordProperties.window__id.value] > 0) |
         (dataframe[RecordProperties.episode__id.value] > 0))
    ]

    # indexes
    indexes = list(dataframe[RecordProperties.window__id.value][dataframe[RecordProperties.window__id.value] != -1].unique())
    indexes.sort()
    return dataframe.copy(), len(indexes), indexes


def computeWindowMetrics(
    dataframe: pd.DataFrame, the_client: str, index: int, required_features: set
):
    """ Computes all the features in `required_features` set and returns a dictionary """

    # separate the dataframe into `window` frames and `episode` frames
    window_df = dataframe[dataframe[RecordProperties.window__id.value] == index]
    episode_df = dataframe[dataframe[RecordProperties.episode__id.value] == index]

    #  sort the dataframes by `frame.timeEpoch`
    window_df = window_df.sort_values(
        by = FrameFields.frame_timeEpoch.value,
        axis = 0,
        ascending = True
    )
    episode_df = episode_df.sort_values(
        by = FrameFields.frame_timeEpoch.value,
        axis = 0,
        ascending = True
    )

    # frames originating at the client
    from_client_df = dataframeFilter_framesFrom(window_df, the_client)
    from_client_df = from_client_df.sort_values(
        by = FrameFields.frame_timeEpoch.value,
        axis = 0,
        ascending = True
    )
    # frames directed at the client
    to_client_df = dataframeFilter_framesTowards(window_df, the_client)
    to_client_df = to_client_df.sort_values(
        by = FrameFields.frame_timeEpoch.value,
        axis = 0,
        ascending = True
    )

    # ***** helper functions *****

    def f__rssi__mean():
        ssi_series = np.asarray(from_client_df[FrameFields.radiotap_dbmAntsignal.value], dtype = np.float64)
        if ssi_series.shape[0] == 0:
            return np.NaN  # drop this record
        return np.nanmean(ssi_series)

    def f__rssi__stddev():
        ssi_series = np.asarray(from_client_df[FrameFields.radiotap_dbmAntsignal.value], dtype = np.float64)
        if ssi_series.shape[0] == 0:
            return np.NaN  # drop this record
        return np.nanstd(ssi_series)

    def f__rssi__linslope():
        ssi_series = np.asarray(from_client_df[FrameFields.radiotap_dbmAntsignal.value], dtype = np.float64)
        epoch_series = np.asarray(from_client_df[FrameFields.frame_timeEpoch.value], dtype = np.float64)
        if ssi_series.shape[0] == 0 or epoch_series.shape[0] == 0:
            return np.NaN  # drop this record
        slope, intercept, r_value, p_value, std_err = linregress(epoch_series, ssi_series)
        return slope

    def f__non_empty_data_frames__rate():
        # data frames (wlan.fc.type_subtype == 0x20 | 0x28) with data.len > 0
        subtype_data_df = from_client_df[
            (
                (from_client_df[FrameFields.data_len.value] > 0) &
                (
                    (from_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.data.value) |
                    (from_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.qos_data.value)
                )
            )
        ].copy()
        # window duration
        window_start, window_end = wp__time_bounds()
        window_duration = math.fabs(window_end - window_start)
        if window_duration == 0:
            return np.NaN  # drop this record
        # rate
        rate = float(subtype_data_df.shape[0]) / window_duration
        return rate

    def f__sleep_frames__binary():
        pwrmgt_set = np.asarray(from_client_df[FrameFields.wlan_fc_pwrmgt.value] == 1, dtype = np.bool)
        sleep = int(np.any(pwrmgt_set))
        return sleep

    def f__empty_null_frames__rate():
        # null frames (wlan.fc.type_subtype == 0x24 | 0x2c) with data.len == 0
        subtype_null_df = from_client_df[
            (
                (from_client_df[FrameFields.data_len.value] == 0) &
                (
                    (from_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.null.value) |
                    (from_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.qos_null.value)
                )
            )
        ].copy()
        # window duration
        window_start, window_end = wp__time_bounds()
        window_duration = math.fabs(window_end - window_start)
        if window_duration == 0:
            return np.NaN  # drop this record
        # rate
        rate = float(subtype_null_df.shape[0]) / window_duration
        return rate

    def f__associated_probe_requests__binary():
        associated_ap = staAssociatedWithClient(window_df, the_client)
        if associated_ap is None:
            return 0
        associated_probe_requests = episode_df[(episode_df[FrameFields.wlan_bssid.value] == associated_ap)]
        return int(associated_probe_requests.shape[0] > 0)

    def f__max_consecutive_beacon_loss__count():
        """
        Maximum number of consecutive beacon frames that are not received according to a
        fixed time interval (assumed 105ms).
        """

        __threshold = 0.105

        associated_ap_bssid = staAssociatedWithClient(dataframe, the_client)
        if associated_ap_bssid is None:
            return -1  # no beacons found, but don't drop the record

        beacons_df = window_df[
            (
                (window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.beacon.value) &
                (window_df[FrameFields.wlan_addr.value].apply(lambda wa: pdFilter_wlanAddrContains(wa, associated_ap_bssid), 0))
            )
        ]

        # sort by `frame.time_epoch`
        beacons_df = beacons_df.sort_values(
            by = FrameFields.frame_timeEpoch.value,
            axis = 0,
            ascending = True
        )

        # time series
        beacon_epoch_series = np.asarray(beacons_df[FrameFields.frame_timeEpoch.value], dtype = np.float64)
        if len(beacon_epoch_series) == 0:
            return -1  # no beacons found, but don't drop the record
        expected_epoch_series = np.arange(beacon_epoch_series[0],
                                          beacon_epoch_series[len(beacon_epoch_series) - 1] + __threshold,
                                          __threshold)

        max_consecutive_beacon_loss_count = 0
        beacon_interval_count = 0
        for current_epoch in expected_epoch_series:
            closest_beacon_delta = np.min(np.absolute(np.subtract(beacon_epoch_series, current_epoch)))
            #
            if closest_beacon_delta < __threshold:
                beacon_interval_count = 0  # reset consecutive loss counter
            else:
                beacon_interval_count += 1  # increase consecutive loss counter
            max_consecutive_beacon_loss_count = max(max_consecutive_beacon_loss_count, beacon_interval_count)
        return max_consecutive_beacon_loss_count

    def f__awake_null_frames__rate():
        # null frames (wlan.fc.type_subtype == 0x24 | 0x2c) with wlan.fc.pwrmgt == 0
        awake_null_df = from_client_df[
            (
                (from_client_df[FrameFields.wlan_fc_pwrmgt.value] == 0) &
                (
                    (from_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.null.value) |
                    (from_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.qos_null.value)
                )
            )
        ].copy()
        # window duration
        window_start, window_end = wp__time_bounds()
        window_duration = math.fabs(window_end - window_start)
        if window_duration == 0:
            return np.NaN  # drop this record
        # rate
        rate = float(awake_null_df.shape[0]) / window_duration
        return rate

    def f__ap_disconnection_frames__binary():
        # disassociation or deathentication frames from the ap
        disconnection_df = to_client_df[
            (
                (to_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.disassociation.value) |
                (to_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.deauthentication.value)
            )
        ].copy()
        return int(disconnection_df.shape[0] > 0)

    def f__client_connection_frames__binary():
        # association req or reassociation req frames from the client
        connection_df = from_client_df[
            (
                (from_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.association_request.value) |
                (from_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.reassociation_request.value)
            )
        ].copy()
        return int(connection_df.shape[0] > 0)

    def f__client_associated__binary():
        return isClientAssociatedWithAp(window_df, the_client)

    def wp__time_bounds():
        start_epoch = float(window_df.head(1)[FrameFields.frame_timeEpoch.value])
        end_epoch = float((window_df.tail(1))[FrameFields.frame_timeEpoch.value])
        return start_epoch, end_epoch

    # ***** map helper functions to features *****
    f__map = {
        WindowMetrics.rssi__mean                        : f__rssi__mean,
        WindowMetrics.rssi__stddev                      : f__rssi__stddev,
        WindowMetrics.rssi__linslope                    : f__rssi__linslope,
        WindowMetrics.non_empty_data_frames__rate       : f__non_empty_data_frames__rate,
        WindowMetrics.sleep_frames__binary              : f__sleep_frames__binary,
        WindowMetrics.empty_null_frames__rate           : f__empty_null_frames__rate,
        WindowMetrics.associated_probe_requests__binary : f__associated_probe_requests__binary,
        WindowMetrics.max_consecutive_beacon_loss__count: f__max_consecutive_beacon_loss__count,
        WindowMetrics.awake_null_frames__rate           : f__awake_null_frames__rate,
        WindowMetrics.ap_disconnection_frames__binary   : f__ap_disconnection_frames__binary,
        WindowMetrics.client_connection_frame__binary   : f__client_connection_frames__binary,
        WindowMetrics.client_associated__binary         : f__client_associated__binary,
    }

    # ***** create output feature dictionary *****
    f__output = dict()
    for key in f__map.keys():
        if key in required_features:
            func = f__map[key]
            f__output[key] = func()

    return f__output
    pass


# def assignRuleBasedTags(episodes_df: pd.DataFrame):
#     """
#     Assigns a 'cause' field to each row of the dataframe with tags for each cause inferred
#     by the rule based checks.
#     """
#
#     def __low_rssi(episode):
#         """
#         For every episode, calculate `mean` and `standard deviation` for rssi value.
#         check: `mean` < -72dB and `std dev` > 12dB
#         """
#
#         if episode[WindowMetrics.rssi__mean.value] < -72 and episode[WindowMetrics.rssi__sd.value] > 12:
#             return True
#         return False
#
#     def __data_frame_loss(episode):
#         """
#         use `fc.retry` field
#         check: #(fc.retry == 1)/#(fc.retry == 1 || fc.retry == 0) > 0.5
#         """
#
#         if episode[WindowMetrics.frame__loss_rate.value] > 0.5:
#             return True
#         return False
#
#     def __power_state_low_to_high_v1(episode):
#         """
#         calculate number of frames per second.
#         check: if #fps > 2
#         """
#
#         _frame_frequency = episode[WindowMetrics.frames__arrival_rate.value]
#         if _frame_frequency == -1:
#             return False
#         elif _frame_frequency > 2:
#             return True
#         return False
#
#     def __power_state_low_to_high_v2(episode):
#         """
#         calculate number of frames per second.
#         check: if #fps <= 2
#         """
#
#         _frame_frequency = episode[WindowMetrics.frames__arrival_rate.value]
#         if _frame_frequency == -1:
#             return False
#         elif _frame_frequency <= 2:
#             return True
#         return False
#
#     def __ap_deauth(episode):
#         """
#         check for deauth packet from ap
#         deauth: fc.type_subtype == 12
#         """
#
#         if episode[WindowMetrics.ap_deauth_frames__count.value] > 0:
#             return True
#         return False
#
#     def __client_deauth(episode):
#         """
#         check for deauth packet from client
#         deauth: fc.type_subtype == 12
#         """
#
#         if episode[WindowMetrics.client_deauth_frames__count.value] > 0:
#             return True
#         return False
#
#     def __beacon_loss(episode):
#         """
#         beacon count is 0 or
#         if beacon interval > 105ms for 7 consecutive beacons or
#         count(wlan.sa = client and type_subtype = 36|44 and pwrmgt = 0) > 0 and count(wlan.ra = client && type_subtype
#  = 29)
#         """
#
#         if (episode[WindowMetrics.beacons__count.value] == 0 or
#                 episode[WindowMetrics.max_consecutive_beacon_loss__count.value] >= 8 or
#                 (episode[WindowMetrics.ack__count.value] == 0 and episode[WindowMetrics.null_frames__count.value] >
#  0)):
#             return True
#         return False
#
#     def __unsuccessful_assoc_auth_reassoc_deauth(episode):
#         if (episode[WindowMetrics.ap_deauth_frames__count.value] > 0 and episode[
#             WindowMetrics.failure_assoc__count.value] == 0):
#             return True
#         return False
#
#     def __successful_assoc_auth_reassoc_deauth(episode):
#         if episode[WindowMetrics.ap_deauth_frames__count.value] == 0 and \
#                 episode[WindowMetrics.success_assoc__count.value] > 0:
#             return True
#         return False
#
#     def __class_3_frames(episode):
#         if episode[WindowMetrics.class_3_frames__count.value] > 0:
#             return True
#         return False
#
#     for idx, _episode in episodes_df.iterrows():
#
#         cause_str = ''
#         if __low_rssi(_episode):
#             cause_str += RBSCauses.low_rssi.value
#
#         if __data_frame_loss(_episode):
#             cause_str += RBSCauses.data_frame_loss.value
#
#         if __power_state_low_to_high_v1(_episode):
#             cause_str += RBSCauses.power_state.value
#
#         if __power_state_low_to_high_v2(_episode):
#             cause_str += RBSCauses.power_state_v2.value
#
#         if __ap_deauth(_episode):
#             cause_str += RBSCauses.ap_side_procedure.value
#
#         if __client_deauth(_episode):
#             cause_str += RBSCauses.client_deauth.value
#
#         if __beacon_loss(_episode):
#             cause_str += RBSCauses.beacon_loss.value
#
#         if __unsuccessful_assoc_auth_reassoc_deauth(_episode):
#             cause_str += RBSCauses.unsuccessful_association.value
#
#         if __successful_assoc_auth_reassoc_deauth(_episode):
#             cause_str += RBSCauses.successful_association.value
#
#         if __class_3_frames(_episode):
#             cause_str += RBSCauses.class_3_frames.value
#
#         episodes_df.loc[idx, 'rbs__cause_tags'] = cause_str
#     return episodes_df


# *****************************************************************************
# *****************************************************************************


def readCsvFile(filepath, error_bad_lines: bool = False, warn_bad_lines: bool = True):
    """
    Read csv file using `pandas` and convert it to a `dataframe`.
    Applies filters and other optimizations while reading to sanitize the data as much as possible.

    :param filepath: path to the csv file
    :param error_bad_lines: raise an error for malformed csv line (False = drop bad lines)
    :param warn_bad_lines: raise a warning for malformed csv line (only if `error_bad_lines` is False)
    :return: dataframe object
    """

    print('• Starting reading file {:s} ...'.format(path.basename(filepath)))

    csv_dataframe = pd.read_csv(
        filepath_or_buffer = filepath,
        sep = '|',  # pipe separated values
        header = 0,  # use first row as column_names
        index_col = None,  # do not use any column to index
        skipinitialspace = True,  # skip any space after delimiter
        na_values = ['', np.NaN, ],  # values to consider as `not available`
        na_filter = True,  # detect `not available` values
        skip_blank_lines = True,  # skip any blank lines in the file
        float_precision = 'high',
        error_bad_lines = error_bad_lines,
        warn_bad_lines = warn_bad_lines
    )

    print('\t', '• Dataframe shape (on read):', csv_dataframe.shape)

    # sanitize data
    # - convert radiotap.dbm_antsignal from a csv field to a float field
    def combineAntennaRssi(ssi_field):
        ssi_values_as_string = str(ssi_field).strip().split(',')
        ssi_values = [float(ssi) for ssi in ssi_values_as_string]
        return np.mean(ssi_values, dtype = np.float64)

    csv_dataframe[FrameFields.radiotap_dbmAntsignal.value] = \
        csv_dataframe[FrameFields.radiotap_dbmAntsignal.value].apply(combineAntennaRssi, 0)
    # drop not available values
    csv_dataframe.dropna(
        axis = 0, subset = [
            FrameFields.frame_timeEpoch.value,
            FrameFields.radiotap_dbmAntsignal.value,
        ],
        inplace = True
    )

    print('\t', '• Dataframe shape (after dropping null values):', csv_dataframe.shape)

    # optimize memory usage
    csv_dataframe[FrameFields.frame_timeEpoch.value] = csv_dataframe[FrameFields.frame_timeEpoch.value].astype(np.float64)
    csv_dataframe[FrameFields.radiotap_datarate.value] = csv_dataframe[FrameFields.radiotap_datarate.value].astype(np.float64, errors = 'ignore')
    csv_dataframe[FrameFields.radiotap_dbmAntsignal.value] = csv_dataframe[FrameFields.radiotap_dbmAntsignal.value].astype(np.float64,
                                                                                                                           errors = 'ignore')
    csv_dataframe[FrameFields.data_len.value] = csv_dataframe[FrameFields.data_len.value].astype(np.int, errors = 'ignore')
    csv_dataframe[FrameFields.wlan_sa.value] = csv_dataframe[FrameFields.wlan_sa.value].astype('category')
    csv_dataframe[FrameFields.wlan_da.value] = csv_dataframe[FrameFields.wlan_da.value].astype('category')
    csv_dataframe[FrameFields.wlan_ta.value] = csv_dataframe[FrameFields.wlan_ta.value].astype('category')
    csv_dataframe[FrameFields.wlan_ra.value] = csv_dataframe[FrameFields.wlan_ra.value].astype('category')
    csv_dataframe[FrameFields.wlan_ssid.value] = csv_dataframe[FrameFields.wlan_ssid.value].astype('category')
    csv_dataframe[FrameFields.wlan_bssid.value] = csv_dataframe[FrameFields.wlan_bssid.value].astype('category')
    csv_dataframe[FrameFields.wlan_fc_pwrmgt.value] = csv_dataframe[FrameFields.wlan_fc_pwrmgt.value].astype('category')
    csv_dataframe[FrameFields.wlan_fc_retry.value] = csv_dataframe[FrameFields.wlan_fc_retry.value].astype('category')
    csv_dataframe[FrameFields.wlan_fc_type.value] = csv_dataframe[FrameFields.wlan_fc_type.value].astype('category')
    csv_dataframe[FrameFields.wlan_fc_typeSubtype.value] = csv_dataframe[FrameFields.wlan_fc_typeSubtype.value].astype('category')
    csv_dataframe[FrameFields.wlan_fixed_statusCode.value] = csv_dataframe[FrameFields.wlan_fixed_statusCode.value].astype('category')

    # sort the dataframe by `frame.timeEpoch`
    csv_dataframe.sort_values(
        by = FrameFields.frame_timeEpoch.value,
        axis = 0,
        ascending = True,
        inplace = True,
        na_position = 'last'
    )
    return csv_dataframe


def windowMetricsAsDataframe(window_characteristics: list, features):
    # merge all dictionaries into one big dictionary
    output_dictionary = dict()
    for _feature in features:
        output_dictionary[_feature.value] = list()

    for _features_dict in window_characteristics:
        for _feature in features:
            output_dictionary[_feature.value].append(_features_dict[_feature])

    # convert to dataframe
    df = pd.DataFrame.from_dict(output_dictionary)
    return df


def processCsvFile(
    source_dir, destination_dir, csv_filename, relevant_clients, relevant_access_points, assign_rbs_tags = False,
    separate_client_files = False
):
    """ Processes a given frame csv file to generate episode characteristics """

    # current time
    timestamp = datetime.datetime.now()

    # read csv file
    csv_filepath = path.join(source_dir, csv_filename)
    main_dataframe = readCsvFile(csv_filepath)
    # csv_file__uuid = timestamp.strftime('%d%m%Y%H%M%S') + '.' + str(uuid4())
    # print('• UUID generated for the file {:s}: {:s}'.format(csv_filename, csv_file__uuid))

    # output column orders
    # semi_processed_output_column_order = main_dataframe.columns.values.tolist()
    # semi_processed_output_column_order.sort()
    # semi_processed_output_column_order.append(EpisodeProperties.episode__id.value)
    # semi_processed_output_column_order.append(EpisodeProperties.associated_client__mac.value)
    # semi_processed_output_column_order.append(EpisodeProperties.csv_file__uuid.value)

    processed_output_column_order = [item.value for item in WindowMetrics.asList()]
    # if assign_rbs_tags:
    #     processed_output_column_order.append('rbs__cause_tags')

    # update mapping file
    # mapping = {
    #     MappingParameters.timestamp__date.value: [timestamp.strftime('%d-%m-%Y'), ],
    #     MappingParameters.timestamp__time.value: [timestamp.strftime('%H-%M-%S'), ],
    #     MappingParameters.frames_file__name.value: [csv_filename, ],
    #     MappingParameters.csv_file__uuid.value: [csv_file__uuid, ],
    # }
    # mapping_df = pd.DataFrame.from_dict(mapping)
    # mapping_columns = mapping_df.columns.values.tolist()
    # mapping_columns.sort()
    # mapping_headers = not path.exists(mapping_file)
    # mapping_df.to_csv(mapping_file, mode = 'a', index = False, header = mapping_headers,
    #                   columns = mapping_columns)

    # all window metrics
    window_metrics_list = list()

    # ### Processing ###
    # 1. keep only relevant frames in memory
    if relevant_clients is not None or relevant_access_points is not None:
        main_dataframe = dataframeFilter_relevantFrames(main_dataframe, relevant_clients, relevant_access_points)
        print("\t", "• MainDataframe shape (keeping only relevant frames):", main_dataframe.shape)

    # 2. for each client...
    if relevant_clients is None:
        relevant_clients = allClientsIn(main_dataframe)

    for the_client in relevant_clients:
        print("\t", "• Processing for client `", the_client, "`")

        # 2.a. copy the main_dataframe
        dataframe = main_dataframe.copy(deep = True)

        # 2.b. filter frames relevant to the_client and the associated_sta only
        the_associated_sta = staAssociatedWithClient(dataframe, the_client)
        if the_associated_sta is not None:
            print("\t\t", "•• Associated STA `", the_associated_sta, "`")
            dataframe = dataframeFilter_relevantFrames2(dataframe, the_client, the_associated_sta)
        else:
            print("\t\t", "•• No associated STA found")
            dataframe = dataframeFilter_relevantFrames2(dataframe, the_client)

        if dataframe is None or dataframe.shape[0] == 0:
            print("\t\t", "•• No relevant frames found for the client `", the_client, "`")
            continue
        else:
            print("\t\t", "•• Dataframe shape (keeping only relevant frames):", dataframe.shape)

        # 2.c. define episodes on frames
        print("\t\t", "•• Creating episodes and window boundaries")
        result = defineEpisodeAndWindowBoundaries(dataframe)
        if result is not None:
            dataframe, count, indexes = result
            print("\t\t", "•• Windows generated for the client:", count)
            if count == 0:
                continue
        else:
            print("\t\t", "•• No Windows were generated for the client")
            continue

        # 2.c.1 save semi_processed csv file for later (can be used to link predictions for episodes back to frames)
        #   - add client to semi processed csv
        #   - add frames file uid to semi processed csv
        # dataframe[EpisodeProperties.associated_client__mac.value] = the_client
        # dataframe[EpisodeProperties.csv_file__uuid.value] = csv_file__uuid
        # # write to file
        # output_csvname = csv_file__uuid + '.csv'
        # output_csvfile = path.join("", output_csvname)
        # dataframe.to_csv(output_csvfile, sep = ',', mode = 'a', index = False, header = True,
        #                  columns = semi_processed_output_column_order)
        # # drop unnecessary columns
        # dataframe.drop(columns = [EpisodeProperties.associated_client__mac.value,
        #                           EpisodeProperties.csv_file__uuid.value], inplace = True)

        # 2.d. for each index...
        for _idx in indexes:
            # 2.d.1. sort the dataframe by `frame.time_epoch`
            dataframe = dataframe.sort_values(
                by = FrameFields.frame_timeEpoch.value,
                axis = 0,
                ascending = True,
            )

            # 2.d.2. compute episode characteristics
            window_metrics = computeWindowMetrics(
                dataframe, the_client, _idx, WindowMetrics.asList()
            )

            # 2.d.4. append to output
            window_metrics_list.append(window_metrics)

    # 3. make a dataframe from window characteristics
    window_characteristics_df = windowMetricsAsDataframe(window_metrics_list, WindowMetrics.asList())
    print("\t", "• Total records generated:", window_characteristics_df.shape[0])
    # 3.a. drop null values, since ML model can't make any sense of this
    non_null_df = window_characteristics_df.dropna(axis = 0)
    print("\t", "• Total records generated (after dropping null values):", non_null_df.shape[0])
    print()

    # 4. (optional) assign tags for causes according to old rule-based-system
    # if assign_rbs_tags:
    #     window_characteristics_df = assign_rbs_tags(window_characteristics_df)

    # 5. generate a csv file as an output
    # if separate_client_files:
    #     for the_client in clients:
    #         _df = window_characteristics_df[
    #             (window_characteristics_df[EpisodeProperties.associated_client__mac.value] == the_client)
    #         ]
    #         name, extension = path.splitext(path.basename(csv_filepath))
    #         output_csvname = str.format('{:s}_{:s}{:s}', name, the_client, extension)
    #         output_csvfile = path.join(destination_dir, output_csvname)
    #         _df.to_csv(output_csvfile, sep = ',', index = False, header = True, columns =
    # processed_output_column_order)
    # else:
    output_csvname = path.basename(csv_filepath)
    output_csvfile = path.join(destination_dir, output_csvname)
    window_characteristics_df.to_csv(output_csvfile, sep = '|', index = False, header = True, columns = processed_output_column_order)


def csv2records(source_dir, destination_dir, relevant_clients, relevant_access_points, assign_rbs_tags,
                separate_client_files):
    for src_dir, _, all_files in walk(source_dir):
        print("Processing directory", path.basename(src_dir))
        print()

        # destination directory
        dst_dir = src_dir.replace(source_dir, destination_dir)
        createDirectoryIfRequired(dst_dir)

        for csv_filename in selectFilesByExtension(src_dir, all_files, csv_extensions):
            processCsvFile(
                source_dir = src_dir,
                destination_dir = dst_dir,
                csv_filename = csv_filename,
                relevant_clients = relevant_clients,
                relevant_access_points = relevant_access_points,
                assign_rbs_tags = assign_rbs_tags,
                separate_client_files = separate_client_files
            )


# *****************************************************************************
# *****************************************************************************


if __name__ == '__main__':
    __source_dir = ProjectDirectory["data.csv"]
    __destination_dir = ProjectDirectory["data.records"]
    envSetup(__source_dir, __destination_dir)

    # apsp
    csv2records(
        source_dir = path.join(__source_dir, "apsp"),
        destination_dir = path.join(__destination_dir, "apsp"),
        relevant_clients = {
            '54:b8:0a:5e:f1:df',
            'c4:12:f5:16:90:64',
            'c4:12:f5:16:90:52',
            '54:b8:0a:5e:ed:47',
            '54:b8:0a:75:e9:e7',
            'c4:12:f5:16:90:4f',
            '74:da:38:35:e9:df',
            '6c:19:8f:b4:bc:6e',
        },
        relevant_access_points = {
            '60:e3:27:49:01:95',
        },
        assign_rbs_tags = False,
        separate_client_files = False
    )

    # bl
    csv2records(
        source_dir = path.join(__source_dir, "bl"),
        destination_dir = path.join(__destination_dir, "bl"),
        relevant_clients = {
            '54:b8:0a:5e:f1:df',
            'c4:12:f5:16:90:64',
            'c4:12:f5:16:90:52',
            '54:b8:0a:5e:ed:47',
            '54:b8:0a:75:e9:e7',
            'c4:12:f5:16:90:4f',
            '74:da:38:35:e9:df',
            '6c:19:8f:b4:bc:6e',
        },
        relevant_access_points = {
            'c4:6e:1f:11:94:b8'
        },
        assign_rbs_tags = False,
        separate_client_files = False
    )

    # ce
    csv2records(
        source_dir = path.join(__source_dir, "ce"),
        destination_dir = path.join(__destination_dir, "ce"),
        relevant_clients = {
            '54:b8:0a:5e:f1:df',
            'c4:12:f5:16:90:64',
            'c4:12:f5:16:90:52',
            '54:b8:0a:5e:ed:47',
            '54:b8:0a:75:e9:e7',
            'c4:12:f5:16:90:4f',
            '74:da:38:35:e9:df',
            '6c:19:8f:b4:bc:6e',
        },
        relevant_access_points = {
            '60:e3:27:49:01:95',
        },
        assign_rbs_tags = False,
        separate_client_files = False
    )

    # lrssi
    csv2records(
        source_dir = path.join(__source_dir, "lrssi"),
        destination_dir = path.join(__destination_dir, "lrssi"),
        relevant_clients = {
            '64:70:02:29:c9:bc',
            '40:49:0f:8a:ae:59',
            '18:4f:32:fb:3e:e7',
        },
        relevant_access_points = {
            '28:c6:8e:db:08:a5',
        },
        assign_rbs_tags = False,
        separate_client_files = False
    )

    # pscan-a
    csv2records(
        source_dir = path.join(__source_dir, "pscan-a"),
        destination_dir = path.join(__destination_dir, "pscan-a"),
        relevant_clients = {
            '10:68:3f:77:f9:b6',
            '30:39:26:96:ba:3e',
            'b4:9c:df:d1:ea:eb',
            '6c:19:8f:b4:bc:6e',
        },
        relevant_access_points = {
            'a0:04:60:aa:78:40',
        },
        assign_rbs_tags = False,
        separate_client_files = False
    )

    # pscan-u
    csv2records(
        source_dir = path.join(__source_dir, "pscan-u"),
        destination_dir = path.join(__destination_dir, "pscan-u"),
        relevant_clients = {
            '5c:f7:e6:a2:5d:14',
            'b4:9c:df:d1:ea:eb',
            'c0:ee:fb:30:d7:17',
            '10:68:3f:77:f9:b6',
            '30:39:26:96:ba:3e',
            '6c:19:8f:b4:bc:6e',
        },
        relevant_access_points = None,
        assign_rbs_tags = False,
        separate_client_files = False
    )

    # pwr
    csv2records(
        source_dir = path.join(__source_dir, "pwr"),
        destination_dir = path.join(__destination_dir, "pwr"),
        relevant_clients = {
            'c0:ee:fb:30:d7:17',
            '10:68:3f:77:f9:b6',
        },
        relevant_access_points = {
            'a0:04:60:aa:78:40',
        },
        assign_rbs_tags = False,
        separate_client_files = False
    )
