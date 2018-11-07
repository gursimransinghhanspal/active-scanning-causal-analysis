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
import argparse
import enum
import math
from collections import defaultdict
from os import path

import numpy as np
import pandas as pd
from scipy.stats import linregress

from globals import (Features, FrameFields, RecordProperties)

__broadcast_bssid = 'ff:ff:ff:ff:ff:ff'

# global dictionary to keep track of client-device association status
# this is updated only using updateClientAssociationStatus()
__association_matrix = defaultdict(lambda: (AssociationStatus.unknown, None))


class AssociationStatus(enum.Enum):
    unknown = enum.auto()
    associated = enum.auto()
    unassociated = enum.auto()


class FrameTypes(enum.Enum):
    management = 0x0
    control = 0x1
    data = 0x2

    @property
    def v(self):
        return self.value


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

    @property
    def v(self):
        return self.value

    # NOTE:
    # The below 3 methods have been defined using the information available in IEEE 802.11 standard v2012
    # refer pages 1012, 1013

    @classmethod
    def pdFilter_class1(cls, the_frame):
        c1_subtypes = [
            # control
            cls.rts.v,
            cls.cts.v,
            cls.ack.v,
            cls.cf_end_cf_ack.v,
            cls.cf_end.v,
            # management
            cls.probe_request.v,
            cls.probe_response.v,
            cls.beacon.v,
            cls.authentication.v,
            cls.deauthentication.v,
            cls.atim.v,
        ]
        #
        # if the_frame's subtype is in defined class1 subtypes, return True
        if the_frame[FrameFields.wlan_fc_typeSubtype.v] in c1_subtypes:
            return True
        #
        # if the_frame has subtype action and its wlan.bssid is empty, return True
        if the_frame[FrameFields.wlan_fc_typeSubtype.v] == cls.action.v:
            if not the_frame[FrameFields.wlan_bssid.v]:
                return True
        #
        return False

    @classmethod
    def pdFilter_class2(cls, the_frame):
        c2_subtypes = [
            cls.association_request.v,
            cls.association_response.v,
            cls.reassociation_request.v,
            cls.reassociation_response.v,
            cls.disassociation.v,
        ]
        #
        # if the_frame's subtype is in defined class2 subtypes, return True
        if the_frame[FrameFields.wlan_fc_typeSubtype.v] in c2_subtypes:
            return True
        #
        return False

    @classmethod
    def pdFilter_class3(cls, the_frame):
        c3_subtypes = [
            cls.ps_poll.v,
            cls.block_ack.v,
            cls.block_ack_request.v,
        ]
        #
        # if the_frame has type data, return True
        if the_frame[FrameFields.wlan_fc_type.v] == FrameTypes.data.v:
            return True
        #
        # if the_frame's subtype is in defined class3 subtypes, return True
        if the_frame[FrameFields.wlan_fc_typeSubtype.v] in c3_subtypes:
            return True
        #
        # if the_frame has subtype action and its wlan.bssid is not empty, return True
        if the_frame[FrameFields.wlan_fc_typeSubtype.v] == cls.action.v:
            if the_frame[FrameFields.wlan_bssid.v]:
                return True
        #
        return False


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


def pdFilter_frameFrom(the_frame, the_src):
    return (
        str(the_frame[FrameFields.wlan_sa.v]).lower() == str(the_src).lower()
        or
        str(the_frame[FrameFields.wlan_ta.v]).lower() == str(the_src).lower()
    )


def pdFilter_frameTowards(the_frame, the_dest):
    return (
        str(the_frame[FrameFields.wlan_da.v]).lower() == str(the_dest).lower()
        or
        str(the_frame[FrameFields.wlan_ra.v]).lower() == str(the_dest).lower()
    )


def dataframeFilter_framesFrom(dataframe, the_src):
    if dataframe is None or dataframe.shape[0] == 0:
        return None

    return dataframe[
        dataframe.apply(lambda the_frame: pdFilter_frameFrom(the_frame, the_src), 1)
    ].copy()


def dataframeFilter_framesTowards(dataframe, the_dest):
    if dataframe is None or dataframe.shape[0] == 0:
        return None

    return dataframe[
        dataframe.apply(lambda the_frame: pdFilter_frameTowards(the_frame, the_dest), 1)
    ].copy()


def dataframeFilter_relevantFrames(dataframe: pd.DataFrame, clients = None, access_points = None):
    """ Filter the frames that belong to only the relevant clients or relevant APs """

    if dataframe is None or dataframe.shape[0] == 0:
        return None

    return dataframe[
        (
            dataframe[FrameFields.wlan_addr.v].apply(lambda wa: pdFilter_wlanAddrContainsAny(wa, clients), 0) |
            dataframe[FrameFields.wlan_addr.v].apply(lambda wa: pdFilter_wlanAddrContainsAny(wa, access_points), 0)
        )
    ].copy()


def dataframeFilter_relevantFrames2(dataframe: pd.DataFrame, client, access_point = None):
    """ Filter the frames that belong to only the relevant clients or relevant APs """

    if dataframe is None or dataframe.shape[0] == 0:
        return None

    return dataframe[
        (
            dataframe[FrameFields.wlan_addr.v].apply(lambda wa: pdFilter_wlanAddrContains(wa, client), 0) |
            dataframe[FrameFields.wlan_addr.v].apply(lambda wa: pdFilter_wlanAddrEquals(wa, {access_point, }), 0)
        )
    ].copy()


# *****************************************************************************
# *****************************************************************************

def allAccessPointsIn(dataframe):
    """
    Retrieve the BSSIDs of all Access Points that can be detected in the given data-the_frame...
    We use the `wlan.bssid` field associated with all the beacon (`wlan.fc.type_subtype` = 8) frames
    """

    if dataframe is None or dataframe.shape[0] == 0:
        return list()

    # filter out only the beacon frames
    beacon_df: pd.DataFrame = dataframe[
        (dataframe[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.beacon.v)
    ].copy()
    if beacon_df is None or beacon_df.shape[0] == 0:
        return list()
    #
    # put all non-null, unique BSSIDs in a list
    bssids_df = beacon_df[FrameFields.wlan_bssid.v].copy()
    bssids_df = bssids_df[bssids_df.notna()]
    bssids = bssids_df.apply(lambda a: str(a).lower(), 0).unique().tolist()
    # remove broadcast address
    if __broadcast_bssid in bssids:
        bssids.remove(__broadcast_bssid)
    return sorted(bssids)


def allClientsIn(dataframe):
    """
    Retrieve the MAC addresses of all client devices that can be detected in the given data-the_frame...
    Only devices who trigger episodes are regarded as clients, so we use probe requests
    """

    if dataframe is None or dataframe.shape[0] == 0:
        return list()

    # filter out only the probe request frames
    probe_request_df = dataframe[
        (dataframe[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.probe_request.v)
    ].copy()
    if probe_request_df is None or probe_request_df.shape[0] == 0:
        return list()
    #
    mac_addrs = set()
    sa_df = probe_request_df[FrameFields.wlan_sa.v].copy()
    sa_df = sa_df[sa_df.notna()]
    sa_df = sa_df.apply(lambda a: str(a).lower(), 0).unique()
    mac_addrs.update(sa_df.values)
    ta_df = probe_request_df[FrameFields.wlan_ta.v].copy()
    ta_df = ta_df[ta_df.notna()]
    ta_df = ta_df.apply(lambda a: str(a).lower(), 0).unique()
    mac_addrs.update(ta_df.values)
    # remove broadcast address
    mac_addrs = mac_addrs.difference({__broadcast_bssid, })
    return sorted(mac_addrs)


def dataframeFilter_class3FramesIn(df, the_client):
    """  """

    if df is None or df.shape[0] == 0:
        return 0

    # all frames originating from the client
    from_client_df = dataframeFilter_framesFrom(df, the_client)
    #
    # filter out only the class3 frames
    class3_df = from_client_df[
        (from_client_df.apply(lambda the_frame: FrameSubtypes.pdFilter_class3(the_frame), 1))
    ].copy()
    return class3_df


def updateClientAssociationStatus(window_df, the_client):
    """
    Updates the client's association status using the window's frames

    :param window_df: all the frames in a window which are relevant to the_client
    :param the_client: the active client's mac_addr
    :return:
    """

    for _idx, the_frame in window_df.iterrows():
        if pdFilter_frameFrom(the_frame, the_client):
            # association
            if the_frame[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.association_request.v:
                __association_matrix[the_client] = (AssociationStatus.associated, the_frame[FrameFields.wlan_bssid.v])
            #
            elif the_frame[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.reassociation_request.v:
                __association_matrix[the_client] = (AssociationStatus.associated, the_frame[FrameFields.wlan_bssid.v])
            #
            # class3
            if FrameSubtypes.pdFilter_class3(the_frame):
                __association_matrix[the_client] = (AssociationStatus.associated, the_frame[FrameFields.wlan_bssid.v])
        #
        elif pdFilter_frameTowards(the_frame, the_client):
            # disassociation
            if the_frame[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.disassociation.v:
                __association_matrix[the_client] = (AssociationStatus.unassociated, None)
            #
            elif the_frame[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.deauthentication.v:
                __association_matrix[the_client] = (AssociationStatus.unassociated, None)
    #
    print("updateClientAssociationStatus:", the_client, __association_matrix[the_client])
    return __association_matrix[the_client]


# *****************************************************************************
# *****************************************************************************


def defineEpisodeAndWindowBoundaries(
    dataframe: pd.DataFrame, true_epochs: np.array = None, true_epoch_threshold = 10
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

    Bundle frames into episodes and windows by assigning a `window_index` field to each the_frame.
    Returns:
        1. dataframe with `window__id` and `episode__id` field
        2. count
        3. indexes
    """

    if dataframe is None or dataframe.shape[0] == 0:
        return None

    # add `window__id` and `episode__id` field to all the frames
    dataframe.loc[:, RecordProperties.window__id.v] = -1
    dataframe.loc[:, RecordProperties.episode__id.v] = -1

    # filter probe request frames
    probe_request_df = dataframe[
        (dataframe[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.probe_request.v)
    ].copy()
    print("\t\t\t", "••• Number of probe requests:", len(probe_request_df))
    # if no probe requests found return
    if probe_request_df is None or probe_request_df.shape[0] == 0:
        return None

    # sort the dataframe by `the_frame.timeEpoch`
    probe_request_df = probe_request_df.sort_values(
        by = FrameFields.frame_timeEpoch.v,
        axis = 0,
        ascending = True
    )

    def pdFilter_trueEpochs(the_epoch):
        deltas = np.absolute(np.subtract(true_epochs, the_epoch))
        mini = np.min(deltas)
        if mini <= true_epoch_threshold:
            return True
        return False

    # filter out true epochs before creating episodes
    if true_epochs is not None:
        probe_request_df = probe_request_df[
            probe_request_df[FrameFields.frame_timeEpoch.v].apply(lambda epoch: pdFilter_trueEpochs(epoch), 0)
        ]
        print("\t\t\t", "••• Number of probe requests (after true epoch filter):", len(probe_request_df))
        # if no probe requests found return
        if probe_request_df is None or probe_request_df.shape[0] == 0:
            return None

    # assign episode ids to probe-requests
    current_episode_id = 1
    previous_epoch = float(probe_request_df[FrameFields.frame_timeEpoch.v].values[0])
    for _idx, series in probe_request_df.iterrows():
        current_epoch = float(series[FrameFields.frame_timeEpoch.v])
        if math.fabs(previous_epoch - current_epoch) >= 1:
            current_episode_id += 1
        # NOTE: assigning directly in the dataframe not the preq view
        dataframe.loc[_idx, RecordProperties.episode__id.v] = current_episode_id
        previous_epoch = current_epoch

    # some metrics regarding episodes
    episode_bounds = list()
    episode_durations = list()
    for _id in range(1, current_episode_id + 1):
        _v = dataframe[dataframe[RecordProperties.episode__id.v] == _id][FrameFields.frame_timeEpoch.v].values
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
            ((dataframe[FrameFields.frame_timeEpoch.v] > _previous_bound[1]) &
             (dataframe[FrameFields.frame_timeEpoch.v] < _current_bound[0])),
            RecordProperties.window__id.v
        ] = _idx

    # this removes frames that could not be assigned to any window or episode
    dataframe[RecordProperties.window__id.v] = dataframe[RecordProperties.window__id.v].astype(int)
    dataframe[RecordProperties.episode__id.v] = dataframe[RecordProperties.episode__id.v].astype(int)
    # dataframe = dataframe[
    #     ((dataframe[RecordProperties.window__id.v] > 0) |
    #      (dataframe[RecordProperties.episode__id.v] > 0))
    # ]

    # indexes
    indexes = list(dataframe[RecordProperties.window__id.v][dataframe[RecordProperties.window__id.v] != -1].unique())
    indexes.sort()
    return dataframe.copy(), len(indexes), indexes


def computeFeaturesUsingIsolatedWindowsAndEpisodes(
    _the_relevant_dataframe: pd.DataFrame, the_client: str, index: int, required_features: set, f__output: dict
):
    # separate the _the_relevant_dataframe into `window` frames and `episode` frames
    _window_df = _the_relevant_dataframe[_the_relevant_dataframe[RecordProperties.window__id.v] == index]
    _episode_df = _the_relevant_dataframe[_the_relevant_dataframe[RecordProperties.episode__id.v] == index]

    # update the client's association status
    updateClientAssociationStatus(_window_df, the_client)

    #  sort the dataframes by `the_frame.timeEpoch`
    _window_df = _window_df.sort_values(
        by = FrameFields.frame_timeEpoch.v,
        axis = 0,
        ascending = True
    )
    _episode_df = _episode_df.sort_values(
        by = FrameFields.frame_timeEpoch.v,
        axis = 0,
        ascending = True
    )

    # frames originating at the client
    _from_client_df = dataframeFilter_framesFrom(_window_df, the_client)
    _from_client_df = _from_client_df.sort_values(
        by = FrameFields.frame_timeEpoch.v,
        axis = 0,
        ascending = True
    )
    # frames directed at the client
    _to_client_df = dataframeFilter_framesTowards(_window_df, the_client)
    _to_client_df = _to_client_df.sort_values(
        by = FrameFields.frame_timeEpoch.v,
        axis = 0,
        ascending = True
    )

    # ***** helper functions *****

    def f__rssi__mean():
        ssi_series = np.asarray(_from_client_df[FrameFields.radiotap_dbmAntsignal.v], dtype = np.float64)
        if ssi_series.shape[0] == 0:
            return np.NaN  # drop this record
        return np.nanmean(ssi_series)

    def f__rssi__stddev():
        ssi_series = np.asarray(_from_client_df[FrameFields.radiotap_dbmAntsignal.v], dtype = np.float64)
        if ssi_series.shape[0] == 0:
            return np.NaN  # drop this record
        return np.nanstd(ssi_series)

    def f__rssi__linslope():
        ssi_series = np.asarray(_from_client_df[FrameFields.radiotap_dbmAntsignal.v], dtype = np.float64)
        epoch_series = np.asarray(_from_client_df[FrameFields.frame_timeEpoch.v], dtype = np.float64)
        if ssi_series.shape[0] == 0 or epoch_series.shape[0] == 0:
            return np.NaN  # drop this record
        slope, intercept, r_value, p_value, std_err = linregress(epoch_series, ssi_series)
        return slope

    def f__non_empty_data_frames__count():
        # data frames (wlan.fc.type_subtype == 0x20 | 0x28) with data.len > 0
        subtype_data_df = _from_client_df[
            (
                (_from_client_df[FrameFields.data_len.v] > 0) &
                (
                    (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.data.v) |
                    (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.qos_data.v)
                )
            )
        ].copy()
        return int(subtype_data_df.shape[0])

    def f__non_empty_data_frames__rate():
        # window duration
        window_duration = math.fabs(rp__window_end__epoch() - rp__window_start__epoch())
        if window_duration == 0:
            return -1
        # rate
        rate = float(f__non_empty_data_frames__count()) / window_duration
        return rate

    def f__sleep_frames__count():
        sleep_df = _from_client_df[
            (_from_client_df[FrameFields.wlan_fc_pwrmgt.v] == 0x01)
        ].copy()
        return int(sleep_df.shape[0])

    def f__sleep_frames__binary():
        return int(f__sleep_frames__count() > 0)

    def f__empty_null_frames__count():
        # null frames (wlan.fc.type_subtype == 0x24 | 0x2c) with data.len <= 0 (< for -1, which is no data)
        subtype_null_df = _from_client_df[
            (
                (_from_client_df[FrameFields.data_len.v] <= 0x00) &
                (
                    (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.null.v) |
                    (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.qos_null.v)
                )
            )
        ].copy()
        return int(subtype_null_df.shape[0])

    def f__empty_null_frames__rate():
        # window duration
        window_duration = math.fabs(rp__window_end__epoch() - rp__window_start__epoch())
        if window_duration == 0:
            return -1
        # rate
        rate = float(f__empty_null_frames__count()) / window_duration
        return rate

    def f__directed_probe_requests__count():
        directed_probe_request_df = _episode_df[
            (_episode_df[FrameFields.wlan_bssid.v] != __broadcast_bssid)
        ]
        return int(directed_probe_request_df.shape[0])

    def f__directed_probe_requests__binary():
        return int(f__directed_probe_requests__count() > 0)

    def f__broadcasted_probe_requests__count():
        broadcast_probe_request_df = _episode_df[
            (_episode_df[FrameFields.wlan_bssid.v] == __broadcast_bssid)
        ]
        return int(broadcast_probe_request_df.shape[0])

    def f__broadcasted_probe_requests__binary():
        return int(f__broadcasted_probe_requests__count() > 0)

    def f__beacon_loss__count():
        __threshold = 0.105

        association_status, associated_ap = __association_matrix[the_client]
        if association_status is AssociationStatus.unknown or association_status is AssociationStatus.unassociated:
            return -1  # no beacons found, but don't drop the record

        beacons_df = _window_df[
            (
                (_window_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.beacon.v) &
                (_window_df[FrameFields.wlan_addr.v].apply(lambda wa: pdFilter_wlanAddrContains(wa, associated_ap), 0))
            )
        ].copy()
        if beacons_df.shape[0] == 0:
            return -2  # no beacons found, but don't drop the record

        # sort by `the_frame.time_epoch`
        beacons_df = beacons_df.sort_values(
            by = FrameFields.frame_timeEpoch.v,
            axis = 0,
            ascending = True
        )

        # time series
        beacon_epoch_series = np.asarray(beacons_df[FrameFields.frame_timeEpoch.v], dtype = np.float64)
        expected_epoch_series = np.arange(beacon_epoch_series[0],
                                          rp__window_end__epoch(),
                                          __threshold)

        beacon_loss_count = 0
        for current_epoch in expected_epoch_series:
            closest_beacon_delta = np.min(np.absolute(np.subtract(beacon_epoch_series, current_epoch)))
            #
            if closest_beacon_delta > __threshold:
                beacon_loss_count += 1  # increase loss counter
        return beacon_loss_count

    def f__awake_null_frames__count():
        # null frames (wlan.fc.type_subtype == 0x24 | 0x2c) with wlan.fc.pwrmgt == 0
        awake_null_df = _from_client_df[
            (
                (_from_client_df[FrameFields.wlan_fc_pwrmgt.v] == 0x00) &
                (
                    (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.null.v) |
                    (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.qos_null.v)
                )
            )
        ].copy()
        return int(awake_null_df.shape[0])

    def f__awake_null_frames__rate():
        # window duration
        window_duration = math.fabs(rp__window_end__epoch() - rp__window_start__epoch())
        if window_duration == 0:
            return -1
        # rate
        rate = float(f__awake_null_frames__count()) / window_duration
        return rate

    def f__sleep_null_frames__count():
        # null frames (wlan.fc.type_subtype == 0x24 | 0x2c) with wlan.fc.pwrmgt == 1
        awake_null_df = _from_client_df[
            (
                (_from_client_df[FrameFields.wlan_fc_pwrmgt.v] == 0x01) &
                (
                    (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.null.v) |
                    (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.qos_null.v)
                )
            )
        ].copy()
        return int(awake_null_df.shape[0])

    def f__sleep_null_frames__rate():
        # window duration
        window_duration = math.fabs(rp__window_end__epoch() - rp__window_start__epoch())
        if window_duration == 0:
            return -1
        # rate
        rate = float(f__sleep_null_frames__count()) / window_duration
        return rate

    def f__ap_disconnection_frames__count():
        # disassociation or deathentication frames to the client
        disconnection_df = _to_client_df[
            (
                (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.disassociation.v) |
                (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.deauthentication.v)
            )
        ].copy()
        return int(disconnection_df.shape[0])

    def f__ap_disconnection_frames__binary():
        return int(f__ap_disconnection_frames__count() > 0)

    def f__client_disconnection_frames__count():
        # disassociation or deathentication frames from the client
        disconnection_df = _from_client_df[
            (
                (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.disassociation.v) |
                (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.deauthentication.v)
            )
        ].copy()
        return int(disconnection_df.shape[0])

    def f__client_disconnection_frames__binary():
        return int(f__client_disconnection_frames__count() > 0)

    def f__client_associated__binary():
        association_status, _ = __association_matrix[the_client]
        if association_status is AssociationStatus.unknown:
            return 0
        elif association_status is AssociationStatus.unassociated:
            return 0
        elif association_status is AssociationStatus.associated:
            return 1
        else:
            return -1

    def f__client_associated__ternary():
        association_status, _ = __association_matrix[the_client]
        if association_status is AssociationStatus.unknown:
            return 2
        elif association_status is AssociationStatus.unassociated:
            return 0
        elif association_status is AssociationStatus.associated:
            return 1
        else:
            return -1

    def f__success_association_response__count():
        success_df = _to_client_df[
            (
                (_to_client_df[FrameFields.wlan_fixed_statusCode.v] == 0x00) &
                (
                    (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.association_response.v) |
                    (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.reassociation_response.v)
                )
            )
        ].copy()
        return int(success_df.shape[0])

    def f__unsuccess_association_response__count():
        unsuccess_df = _to_client_df[
            (
                (_to_client_df[FrameFields.wlan_fixed_statusCode.v] != 0x00) &
                (
                    (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.association_response.v) |
                    (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.reassociation_response.v)
                )
            )
        ].copy()
        return int(unsuccess_df.shape[0])

    def f__class3_frames__count():
        c3_df = _window_df[
            (_window_df.apply(lambda the_frame: FrameSubtypes.pdFilter_class3(the_frame), 1))
        ].copy()
        return int(c3_df.shape[0])

    def f__client_frames__rate():
        # frames originating at the_client
        num_frames = float(_from_client_df.shape[0])
        if _from_client_df.shape[0] == 0:
            return -1

        # duration
        time_head = float(_from_client_df.head(1)[FrameFields.frame_timeEpoch.v])
        time_tail = float(_from_client_df.tail(1)[FrameFields.frame_timeEpoch.v])
        time_diff = math.fabs(time_tail - time_head)

        if time_diff == 0:
            return -2
        # rate
        rate = float(num_frames / time_diff)
        return rate

    def f__ap_deauth__count():
        deauth_df = _to_client_df[
            (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.deauthentication.v)
        ].copy()
        return int(deauth_df.shape[0])

    def f__ack__count():
        ack_df = _to_client_df[
            (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.ack.v)
        ].copy()
        return int(ack_df.shape[0])

    def f__retry__ratio():
        fresh_df = _from_client_df[
            (_from_client_df[FrameFields.wlan_fc_retry.v] == 0x00)
        ].copy()
        retry_df = _from_client_df[
            (_from_client_df[FrameFields.wlan_fc_retry.v] == 0x01)
        ].copy()
        #
        total_count = fresh_df.shape[0] + retry_df.shape[0]
        if total_count == 0:
            return -1
        ratio = float(retry_df.shape[0]) / float(total_count)
        return ratio

    def f__client_deauth__count():
        deauth_df = _from_client_df[
            (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.deauthentication.v)
        ].copy()
        return int(deauth_df.shape[0])

    #
    #

    def rp__window_start__epoch():
        start_epoch = float(_window_df.head(1)[FrameFields.frame_timeEpoch.v])
        return start_epoch

    def rp__window_end__epoch():
        end_epoch = float((_window_df.tail(1))[FrameFields.frame_timeEpoch.v])
        return end_epoch

    def rp__episode_start__epoch():
        start_epoch = float(_episode_df.head(1)[FrameFields.frame_timeEpoch.v])
        return start_epoch

    def rp__episode_end__epoch():
        end_epoch = float((_episode_df.tail(1))[FrameFields.frame_timeEpoch.v])
        return end_epoch

    # ***** map helper functions to features *****
    f__map = {
        Features.rssi__mean                           : f__rssi__mean,
        Features.rssi__stddev                         : f__rssi__stddev,
        Features.rssi__linslope                       : f__rssi__linslope,
        Features.non_empty_data_frames__count         : f__non_empty_data_frames__count,
        Features.non_empty_data_frames__rate          : f__non_empty_data_frames__rate,
        Features.sleep_frames__count                  : f__sleep_frames__count,
        Features.sleep_frames__binary                 : f__sleep_frames__binary,
        Features.empty_null_frames__count             : f__empty_null_frames__count,
        Features.empty_null_frames__rate              : f__empty_null_frames__rate,
        Features.directed_probe_requests__count       : f__directed_probe_requests__count,
        Features.directed_probe_requests__binary      : f__directed_probe_requests__binary,
        Features.broadcasted_probe_requests__count    : f__broadcasted_probe_requests__count,
        Features.broadcasted_probe_requests__binary   : f__broadcasted_probe_requests__binary,
        Features.beacon_loss__count                   : f__beacon_loss__count,
        Features.awake_null_frames__count             : f__awake_null_frames__count,
        Features.awake_null_frames__rate              : f__awake_null_frames__rate,
        Features.sleep_null_frames__count             : f__sleep_null_frames__count,
        Features.sleep_null_frames__rate              : f__sleep_null_frames__rate,
        Features.ap_disconnection_frames__count       : f__ap_disconnection_frames__count,
        Features.ap_disconnection_frames__binary      : f__ap_disconnection_frames__binary,
        Features.client_disconnection_frames__count   : f__client_disconnection_frames__count,
        Features.client_disconnection_frames__binary  : f__client_disconnection_frames__binary,
        Features.client_associated__binary            : f__client_associated__binary,
        Features.client_associated__ternary           : f__client_associated__ternary,
        Features.success_association_response__count  : f__success_association_response__count,
        Features.unsuccess_association_response__count: f__unsuccess_association_response__count,
        Features.class3_frames__count                 : f__class3_frames__count,
        Features.client_frames__rate                  : f__client_frames__rate,
        Features.ap_deauth__count                     : f__ap_deauth__count,
        Features.ack__count                           : f__ack__count,
        Features.retry__ratio                         : f__retry__ratio,
        Features.client_deauth__count                 : f__client_deauth__count,
        #
        ##
        #
        RecordProperties.window__id                   : lambda: index,
        RecordProperties.window_start__epoch          : rp__window_start__epoch,
        RecordProperties.window_end__epoch            : rp__window_end__epoch,
        RecordProperties.window_duration__seconds     : lambda: math.fabs(rp__window_end__epoch() - rp__window_start__epoch()),
        RecordProperties.window_frames__count         : lambda: _window_df.shape[0],
        RecordProperties.relevant_client__mac         : lambda: str(the_client),
        RecordProperties.episode__id                  : lambda: index,
        RecordProperties.episode_start__epoch         : rp__episode_start__epoch,
        RecordProperties.episode_end__epoch           : rp__episode_end__epoch,
        RecordProperties.episode_duration__seconds    : lambda: math.fabs(rp__episode_end__epoch() - rp__episode_start__epoch()),
        RecordProperties.episode_frames__count        : lambda: _episode_df.shape[0],

        # NOTE: this method does not define all RecordProperties exhaustively
    }

    # ***** create output feature dictionary *****
    for key in f__map.keys():
        if key in required_features:
            func = f__map[key]
            f__output[key] = func()

    return f__output


def computeFeaturesUsingMultipleWindows(
    _the_relevant_dataframe: pd.DataFrame, the_client: str, indexes: list, required_features: set, f__output: list
):
    # frames originating at the client
    _from_client_df = dataframeFilter_framesFrom(_the_relevant_dataframe, the_client)
    _from_client_df = _from_client_df.sort_values(
        by = FrameFields.frame_timeEpoch.v,
        axis = 0,
        ascending = True
    )
    # frames directed at the client
    _to_client_df = dataframeFilter_framesTowards(_the_relevant_dataframe, the_client)
    _to_client_df = _to_client_df.sort_values(
        by = FrameFields.frame_timeEpoch.v,
        axis = 0,
        ascending = True
    )

    # episode mean time epochs
    episode_mean_epochs = np.zeros((len(indexes),), dtype = np.float)
    for _i, _idx in enumerate(indexes):
        episode_df = _the_relevant_dataframe[
            (_the_relevant_dataframe[RecordProperties.episode__id.v] == _idx)
        ].copy()
        #
        mean_epoch = np.nanmean(episode_df[FrameFields.frame_timeEpoch.v])
        episode_mean_epochs[_i] = mean_epoch

    def f__client_connection_request_frames__count(__connection_threshold):
        conn_req_df = _from_client_df[
            (
                (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.association_request.v) |
                (_from_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.reassociation_request.v)
            )
        ].copy()
        #
        counts = np.zeros_like(episode_mean_epochs)
        for _, the_frame in conn_req_df.iterrows():
            deltas = np.absolute(np.subtract(episode_mean_epochs, float(the_frame[FrameFields.frame_timeEpoch.v])))
            mini = np.argmin(deltas)
            if deltas[mini] <= __connection_threshold:
                counts[mini] += 1
        #
        return counts

    def f__client_connection_request_frames__binary(__connection_threshold):
        counts = f__client_connection_request_frames__count(__connection_threshold)
        bincounts = np.zeros_like(counts)
        for _j, count in enumerate(counts):
            bincounts[_j] = int(count > 0)
        return bincounts

    def f__client_connection_response_frames__count(__connection_threshold):
        conn_res_df = _to_client_df[
            (
                (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.association_response.v) |
                (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.reassociation_response.v)
            )
        ].copy()
        #
        counts = np.zeros_like(episode_mean_epochs)
        for _, the_frame in conn_res_df.iterrows():
            deltas = np.absolute(np.subtract(episode_mean_epochs, float(the_frame[FrameFields.frame_timeEpoch.v])))
            mini = np.argmin(deltas)
            if deltas[mini] <= __connection_threshold:
                counts[mini] += 1
        #
        return counts

    def f__client_connection_response_frames__binary(__connection_threshold):
        counts = f__client_connection_response_frames__count(__connection_threshold)
        bincounts = np.zeros_like(counts)
        for _j, count in enumerate(counts):
            bincounts[_j] = int(count > 0)
        return bincounts

    def f__client_connection_success_response_frames__count(__connection_threshold):
        success_conn_res_df = _to_client_df[
            (
                (
                    (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.association_response.v) |
                    (_to_client_df[FrameFields.wlan_fc_typeSubtype.v] == FrameSubtypes.reassociation_response.v)
                ) &
                (_to_client_df[FrameFields.wlan_fixed_statusCode.v] == 0x00)
            )
        ].copy()
        #
        counts = np.zeros_like(episode_mean_epochs)
        for _, the_frame in success_conn_res_df.iterrows():
            deltas = np.absolute(np.subtract(episode_mean_epochs, float(the_frame[FrameFields.frame_timeEpoch.v])))
            mini = np.argmin(deltas)
            if deltas[mini] <= __connection_threshold:
                counts[mini] += 1
        #
        return counts

    def f__client_connection_success_response_frames__binary(__connection_threshold):
        counts = f__client_connection_success_response_frames__count(__connection_threshold)
        bincounts = np.zeros_like(counts)
        for _j, count in enumerate(counts):
            bincounts[_j] = int(count > 0)
        return bincounts

    # ***** map helper functions to features *****
    f__map = {
        Features.client_connection_request_frames__count_1          : lambda: f__client_connection_request_frames__count(1),
        Features.client_connection_request_frames__binary_1         : lambda: f__client_connection_request_frames__binary(1),
        Features.client_connection_response_frames__count_1         : lambda: f__client_connection_response_frames__count(1),
        Features.client_connection_response_frames__binary_1        : lambda: f__client_connection_response_frames__binary(1),
        Features.client_connection_success_response_frames__count_1 : lambda: f__client_connection_success_response_frames__count(1),
        Features.client_connection_success_response_frames__binary_1: lambda: f__client_connection_success_response_frames__binary(1),

        Features.client_connection_request_frames__count_3          : lambda: f__client_connection_request_frames__count(3),
        Features.client_connection_request_frames__binary_3         : lambda: f__client_connection_request_frames__binary(3),
        Features.client_connection_response_frames__count_3         : lambda: f__client_connection_response_frames__count(3),
        Features.client_connection_response_frames__binary_3        : lambda: f__client_connection_response_frames__binary(3),
        Features.client_connection_success_response_frames__count_3 : lambda: f__client_connection_success_response_frames__count(3),
        Features.client_connection_success_response_frames__binary_3: lambda: f__client_connection_success_response_frames__binary(3),

        Features.client_connection_request_frames__count_5          : lambda: f__client_connection_request_frames__count(5),
        Features.client_connection_request_frames__binary_5         : lambda: f__client_connection_request_frames__binary(5),
        Features.client_connection_response_frames__count_5         : lambda: f__client_connection_response_frames__count(5),
        Features.client_connection_response_frames__binary_5        : lambda: f__client_connection_response_frames__binary(5),
        Features.client_connection_success_response_frames__count_5 : lambda: f__client_connection_success_response_frames__count(5),
        Features.client_connection_success_response_frames__binary_5: lambda: f__client_connection_success_response_frames__binary(5),
    }

    # ***** create output list of feature dictionaries *****
    for key in f__map.keys():
        if key in required_features:
            func = f__map[key]
            output_arr = func()
            for _j, _idx in enumerate(indexes):
                f__output[_j][key] = output_arr[_j]

    return f__output


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

    print("->>> readCsvFile")
    #
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
        return np.nanmean(ssi_values, dtype = np.float64)

    csv_dataframe[FrameFields.radiotap_dbmAntsignal.v] = \
        csv_dataframe[FrameFields.radiotap_dbmAntsignal.v].apply(combineAntennaRssi, 0)

    # • Handle null values
    drop_na_fields = [
        FrameFields.frame_timeEpoch.v,
        FrameFields.radiotap_dbmAntsignal.v,
    ]
    replace_na = [
        (FrameFields.data_len, -1),
        (FrameFields.wlan_fc_pwrmgt, -1),
        (FrameFields.wlan_fc_retry, -1),
        (FrameFields.wlan_fc_type, -1),
        (FrameFields.wlan_fc_typeSubtype, -1),
        (FrameFields.wlan_fixed_statusCode, -1),
    ]

    # -- drop null values
    csv_dataframe.dropna(
        axis = 0, subset = drop_na_fields,
        inplace = True
    )
    print('\t', '• Dataframe shape (after dropping null values):', csv_dataframe.shape)
    #
    for f, v in replace_na:
        csv_dataframe[f.v] = csv_dataframe[f.v].fillna(v)

    # • Optimize memory usage
    floats = [
        FrameFields.frame_timeEpoch,
        FrameFields.radiotap_dbmAntsignal,
    ]
    ints = [
        FrameFields.data_len,
    ]
    categories = [
        FrameFields.wlan_addr,
        FrameFields.wlan_da,
        FrameFields.wlan_ra,
        FrameFields.wlan_sa,
        FrameFields.wlan_ta,
        FrameFields.wlan_bssid,
        FrameFields.wlan_fc_pwrmgt,
        FrameFields.wlan_fc_retry,
        FrameFields.wlan_fc_type,
        FrameFields.wlan_fc_typeSubtype,
        FrameFields.wlan_fixed_statusCode,
    ]

    for f in floats:
        csv_dataframe[f.v] = csv_dataframe[f.v].astype(np.float, errors = 'ignore')
    for f in ints:
        csv_dataframe[f.v] = csv_dataframe[f.v].astype(np.int, errors = 'ignore')
    for f in categories:
        csv_dataframe[f.v] = csv_dataframe[f.v].astype('category', errors = 'ignore')

    # sort the dataframe by `the_frame.timeEpoch`
    csv_dataframe.sort_values(
        by = FrameFields.frame_timeEpoch.v,
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
        output_dictionary[_feature.v] = list()

    for _features_dict in window_characteristics:
        for _feature in features:
            output_dictionary[_feature.v].append(_features_dict[_feature])

    # convert to dataframe
    df = pd.DataFrame.from_dict(output_dictionary)
    return df


def processCsvFile(
    infile,
    outfile,
    relevant_clients, relevant_access_points,
    epoch_filter_per_client,
    epoch_filter_threshold,
):
    """ Processes a given the_frame csv file to generate episode characteristics """

    # read csv file
    main_dataframe = readCsvFile(infile)

    # the output columns
    output_columns = Features.asList() + RecordProperties.asList()
    output_column_values = Features.valuesAsList() + RecordProperties.valuesAsList()

    # ### Processing ###
    # 1. keep only relevant frames in memory
    if relevant_clients is not None or relevant_access_points is not None:
        main_dataframe = dataframeFilter_relevantFrames(main_dataframe, relevant_clients, relevant_access_points)
        print("\t", "• MainDataframe shape (keeping only relevant frames):", main_dataframe.shape)

    # 2. for each client...
    if relevant_clients is None:
        relevant_clients = allClientsIn(main_dataframe)

    # initialize associated AP for each client
    # for the_client in relevant_clients:
    #     initClientAssociationStatus(main_dataframe, the_client)

    metrics_list = list()

    for the_client in relevant_clients:
        print("\t", "• Processing for client `", the_client, "`")

        # 2.a. copy the main_dataframe
        the_client_relevant_dataframe = main_dataframe.copy(deep = True)

        # 2.b. filter frames relevant to the_client and the associated_sta only
        association_status, the_associated_ap = __association_matrix[the_client]
        if association_status is AssociationStatus.unknown:
            print("\t\t", "•• Association Status is Unknown")
            the_client_relevant_dataframe = dataframeFilter_relevantFrames2(the_client_relevant_dataframe, the_client)
        #
        elif association_status is AssociationStatus.unassociated:
            print("\t\t", "•• Not associated to an Access Point")
            the_client_relevant_dataframe = dataframeFilter_relevantFrames2(the_client_relevant_dataframe, the_client)
        #
        elif association_status is AssociationStatus.associated:
            print("\t\t", "•• Associated Access Point: `", the_associated_ap, "`")
            the_client_relevant_dataframe = dataframeFilter_relevantFrames2(the_client_relevant_dataframe, the_client, the_associated_ap)
        #
        else:
            print("\t\t", "•• Invalid Status")

        if the_client_relevant_dataframe is None or the_client_relevant_dataframe.shape[0] == 0:
            print("\t\t", "•• No relevant frames found for the client `", the_client, "`")
            continue
        else:
            print("\t\t", "•• Dataframe shape (keeping only relevant frames):", the_client_relevant_dataframe.shape)

        # 2.c. define episodes on frames
        print("\t\t", "•• Creating episodes and window boundaries")
        result = defineEpisodeAndWindowBoundaries(
            the_client_relevant_dataframe, epoch_filter_per_client[the_client], epoch_filter_threshold
        )
        if result is not None:
            the_client_relevant_dataframe, count, indexes = result
            print("\t\t", "•• Windows generated for the client:", count)
            if count == 0:
                continue
        else:
            print("\t\t", "•• No Windows were generated for the client")
            continue

        # 2.d. for each index...
        client_metrics_list = list()

        for _idx in indexes:
            # 2.d.1. sort the dataframe by `the_frame.time_epoch`
            the_client_relevant_dataframe = the_client_relevant_dataframe.sort_values(
                by = FrameFields.frame_timeEpoch.v,
                axis = 0,
                ascending = True,
            )

            # 2.d.2. compute episode characteristics
            isolated_window_metrics = {
                RecordProperties.csv_file__name   : path.basename(infile),
                RecordProperties.csv_file__relpath: path.relpath(infile, path.abspath("../../data/csv")),
            }
            isolated_window_metrics = computeFeaturesUsingIsolatedWindowsAndEpisodes(
                the_client_relevant_dataframe, the_client, _idx, output_columns, isolated_window_metrics
            )

            # 2.d.4. append to output
            client_metrics_list.append(isolated_window_metrics)

        # compute using entire df
        client_metrics_list = computeFeaturesUsingMultipleWindows(
            the_client_relevant_dataframe, the_client, indexes, output_columns, client_metrics_list
        )
        # add to the final list
        metrics_list.extend(client_metrics_list)

    # 3. make a dataframe from window characteristics
    window_characteristics_df = windowMetricsAsDataframe(metrics_list, output_columns)
    print("\t", "• Total records generated:", window_characteristics_df.shape[0])
    window_characteristics_df.to_csv(outfile, sep = '|', index = False, header = True, columns = output_column_values)


# *****************************************************************************
# *****************************************************************************

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ifile", required = True)
    parser.add_argument("--ofile", required = True)
    parser.add_argument("--clients", required = False)
    parser.add_argument("--epoch_filters", required = False)
    parser.add_argument("--access_points", required = False)
    args = parser.parse_args()
    #
    ifile = path.abspath(args.ifile)
    ofile = path.abspath(args.ofile)
    clients = str(args.clients).split(",") if args.clients else None
    epoch_files = str(args.epoch_filters).split(",") if args.epoch_filters else None
    aps = str(args.access_points).split(",") if args.access_points else None
    #
    print(epoch_files)
    epoch_per_client = defaultdict(lambda: None)
    if epoch_files is not None:
        for i, loc in enumerate(epoch_files):
            filepath = path.abspath(loc)
            df = pd.read_csv(filepath, sep = ",", header = None, index_col = None)
            nd = np.asarray(df[0], dtype = np.float64)
            nd = np.divide(nd, 1000)
            epoch_per_client[clients[i]] = nd.copy()
    #
    if clients:
        clients = set(clients)
    if aps:
        aps = set(aps)
    #
    processCsvFile(
        infile = path.abspath(args.ifile),
        outfile = path.abspath(args.ofile),
        relevant_clients = clients,
        relevant_access_points = aps,
        epoch_filter_per_client = epoch_per_client,
        epoch_filter_threshold = 2  # 2 second threshold
    )
