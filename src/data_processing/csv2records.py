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
from os import path
from uuid import uuid4

import numpy as np
import pandas as pd
from scipy.stats import linregress

from globals import (DefaultDirectory, EpisodeProperties, FrameFields, FrameSubtypes, MLFeatures,
                     WindowMetrics, WindowProperties, class_3_frames_subtypes, csv_extensions, )
from src import aux


# *****************************************************************************
# *****************************************************************************

def relevanceFilter(dataframe: pd.DataFrame, clients: list, access_points: list = None):
    """ Filter out the rows (frames) that are not relevant to the process. """

    # Filter to accept if
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
        print('• Using access points to filter beacon packets. Access points:', access_points)

        _df = dataframe[
            (
                    (dataframe[FrameFields.wlan_sa.value].isin(clients)) |
                    (dataframe[FrameFields.wlan_da.value].isin(clients)) |
                    (dataframe[FrameFields.wlan_ta.value].isin(clients)) |
                    (dataframe[FrameFields.wlan_ra.value].isin(clients)) |
                    (
                            (dataframe[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.beacon.value) &
                            (
                                    (dataframe[FrameFields.wlan_bssid.value].isin(access_points)) |
                                    (dataframe[FrameFields.wlan_ta.value].isin(access_points))
                            )
                    )
            )
        ]
    else:
        _df = dataframe[
            (
                    (dataframe[FrameFields.wlan_sa.value].isin(clients)) |
                    (dataframe[FrameFields.wlan_da.value].isin(clients)) |
                    (dataframe[FrameFields.wlan_ta.value].isin(clients)) |
                    (dataframe[FrameFields.wlan_ra.value].isin(clients)) |
                    (dataframe[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.beacon.value)
            )
        ]

    if len(_df) == 0:
        return None
    return _df


def filterByMacAddress(dataframe: pd.DataFrame, client_mac: str):
    """ Filter out the rows (frames) that do not associate with the given client """

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
        (
                (dataframe[FrameFields.wlan_sa.value] == client_mac) |
                (dataframe[FrameFields.wlan_da.value] == client_mac) |
                (dataframe[FrameFields.wlan_ta.value] == client_mac) |
                (dataframe[FrameFields.wlan_ra.value] == client_mac) |
                (dataframe[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.beacon.value)
        )
    ]

    if len(_df) == 0:
        return None
    return _df


def apAssociatedToClient(dataframe, the_client):
    """
    Returns the mac address of the access point the client is connected to.
    If could not be determined, returns None

    :param the_client:
    :param dataframe:
    :return:
    """

    client_df = dataframe[
        (dataframe[FrameFields.wlan_sa.value] == the_client)
    ]

    associated_bssid = set()
    associated_bssid.update(
        set(client_df[FrameFields.wlan_bssid.value][client_df[FrameFields.wlan_bssid.value].notna()].unique())
    )
    associated_bssid = associated_bssid.difference({'ff:ff:ff:ff:ff:ff', })
    associated_bssid = list(associated_bssid)

    # if uniquely identifiable, great
    if len(associated_bssid) == 1:
        return associated_bssid[0]

    # else, return the one with max count
    if len(associated_bssid) > 1:
        associated_bssid_list = client_df[FrameFields.wlan_bssid.value].tolist()
        max_counted = (0, None)
        for bssid in associated_bssid:
            count = associated_bssid_list.count(bssid)
            if count > max_counted[0]:
                max_counted = (count, bssid)
        return max_counted[1]

    return None


def allAccessPointsIn(dataframe):
    """ Returns a list of all access points' mac addresses (bssid) """

    print('• Extracting mac addresses for all the access points present in the file')

    # look at only beacons
    _beacon_df = dataframe[(dataframe[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.beacon.value)]
    #
    access_points_bssid = set()
    access_points_bssid.update(
        set(_beacon_df[FrameFields.wlan_bssid.value][_beacon_df[FrameFields.wlan_bssid.value].notna()].unique())
    )
    del _beacon_df

    # remove `broadcast`
    access_points_bssid = access_points_bssid.difference({'ff:ff:ff:ff:ff:ff', })

    # convert to list
    access_points_bssid = list(access_points_bssid)
    access_points_bssid.sort()
    print('\t', '•• Found {:d} unique mac addresses'.format(len(access_points_bssid)))
    return access_points_bssid


def allClientsIn(dataframe):
    """ Returns a list of all the clients that sent out probe requests """

    print('• Extracting mac addresses for all the clients present in the file')

    # look at only probe requests
    _preq_df = dataframe[(dataframe[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.probe_request.value)]
    #
    client_mac_addresses = set()
    client_mac_addresses.update(set(
        _preq_df[FrameFields.wlan_sa.value][_preq_df[FrameFields.wlan_sa.value].notna()].unique()
    ))
    client_mac_addresses.update(set(
        _preq_df[FrameFields.wlan_ta.value][_preq_df[FrameFields.wlan_ta.value].notna()].unique()
    ))
    del _preq_df

    # remove `broadcast`
    client_mac_addresses = client_mac_addresses.difference({'ff:ff:ff:ff:ff:ff', })

    # convert to list
    client_mac_addresses = list(client_mac_addresses)
    client_mac_addresses.sort()
    print('\t', '•• Found {:d} unique mac addresses'.format(len(client_mac_addresses)))
    return client_mac_addresses


def csvColumnNames(features):
    order = [item.value for item in features]
    return order


def windowCharacteristicsAsDataframe(window_characteristics: list, features):
    """ Creates a dataframe from a list of 2-tuples containing ep_features and ep_properties """

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


# *****************************************************************************
# *****************************************************************************


def defineLinearTrendForBeacons(dataframe, ap_bssid_list):
    ap_trends = dict()
    for bssid in ap_bssid_list:
        _df = dataframe[
            (
                    (dataframe[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.beacon.value) &
                    (
                            (dataframe[FrameFields.wlan_bssid.value] == bssid) |
                            (dataframe[FrameFields.wlan_sa.value] == bssid)
                    )
            )
        ]

        _df.sort_values(
            by = FrameFields.frame_timeEpoch.value,
            axis = 0,
            ascending = True,
            inplace = True,
            na_position = 'last'
        )

        _epoch_series = _df[FrameFields.frame_timeEpoch.value]
        _beacon_cdf = np.cumsum(np.ones(_epoch_series.shape[0]))
        lin_reg = linregress(_epoch_series, _beacon_cdf)
        ap_trends[bssid] = lin_reg

    return ap_trends


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
      using a window of frames that precedes the AS episode. This window extends from the start of current episode
      till the end of the previous episode of AS by the same client.

    Bundle frames into episodes and windows by assigning a `window_index` field to each frame.
    Returns:
        1. dataframe with `window__id` and `episode__id` field
        2. count
        3. indexes
    """

    # filter: packet type = `probe request`
    _df_preqs = dataframe[dataframe[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.probe_request.value]
    print('\t', '• Number of probe requests:', len(_df_preqs))
    # if no probe requests found return
    if len(_df_preqs) == 0:
        return None

    # sort the dataframe by `frame.timeEpoch`
    _df_preqs.sort_values(
        by = FrameFields.frame_timeEpoch.value,
        axis = 0,
        ascending = True,
        inplace = True,
        na_position = 'last'
    )

    # filter out true epochs before creating episodes
    if true_episode_epochs is not None:
        true_epoch_filter = np.zeros(_df_preqs.shape[0])
        for _idx, series in _df_preqs.iterrows():
            true_epoch_filter[_idx] = np.any(
                np.absolute(true_episode_epochs - float(series[FrameFields.frame_timeEpoch.value]))
                <= true_epoch_delta_threshold
            )
        _df_preqs = _df_preqs[true_epoch_filter]
        print('\t', '• Number of probe requests (after true epoch filter):', len(_df_preqs))

    # define event start and end boundaries
    # NOTE: event = window + episode
    event_bounds = list()
    current_event_bounds = [0, ]
    previous_epoch = 0
    for _idx, series in _df_preqs.iterrows():
        current_epoch = float(series[FrameFields.frame_timeEpoch.value])
        if abs(current_epoch - previous_epoch) > 1:
            current_event_bounds.append(previous_epoch)
            event_bounds.append(tuple(current_event_bounds))
            current_event_bounds = [current_epoch, ]
        previous_epoch = current_epoch
    del _df_preqs

    # some metrics regarding episodes
    _ep_durations = [abs(a - b) for a, b in event_bounds]
    _ep_durations = np.array(_ep_durations)
    print('\t', '•• Number of episodes:', str(_ep_durations.shape[0]))
    print('\t', '•• Max episode duration:', str(_ep_durations.max()))
    print('\t', '•• Mean episode duration:', str(_ep_durations.mean()))
    print('\t', '•• Std. dev for episode duration:', str(_ep_durations.std()))

    # add `window__id` and `episode__id` field to all the frames
    dataframe.loc[:, WindowProperties.window__id.value] = -1
    dataframe.loc[:, EpisodeProperties.episode__id.value] = -1
    # give sensible `window__id` and `episode__id` to respective frames
    # NOTE: `window__id` and `episode__id` start from 1 not 0.
    for _idx in range(1, len(event_bounds)):
        _previous_bound = event_bounds[_idx - 1]
        _current_bound = event_bounds[_idx]

        dataframe.loc[
            ((dataframe[FrameFields.frame_timeEpoch.value] > _previous_bound[1]) &
             (dataframe[FrameFields.frame_timeEpoch.value] < _current_bound[0])),
            WindowProperties.window__id.value
        ] = _idx

        dataframe.loc[
            ((dataframe[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.probe_request.value) &
             (dataframe[FrameFields.frame_timeEpoch.value] >= _current_bound[0]) &
             (dataframe[FrameFields.frame_timeEpoch.value] <= _current_bound[1])),
            EpisodeProperties.episode__id.value
        ] = _idx

    # this removes frames that could not be assigned to any window or episode
    dataframe[WindowProperties.window__id.value] = dataframe[WindowProperties.window__id.value].astype(int)
    dataframe[EpisodeProperties.episode__id.value] = dataframe[EpisodeProperties.episode__id.value].astype(int)
    dataframe = dataframe[
        ((dataframe[WindowProperties.window__id.value] > 0) |
         (dataframe[EpisodeProperties.episode__id.value] > 0))
    ]

    # indexes
    indexes = list(dataframe[WindowProperties.window__id.value].unique())
    indexes.sort()
    return dataframe, len(indexes), indexes


def computeFeaturesAndProperties(
        dataframe: pd.DataFrame, the_client: str, index: int, ap_beacon_count_linear_trends: dict,
        required_features: set
):
    """ Computes all the features in `required_features` set and returns a dictionary """

    # separate the dataframe into `window` frames and `episode` frames
    window_df = dataframe[dataframe[WindowProperties.window__id.value] == index]
    episode_df = dataframe[dataframe[EpisodeProperties.episode__id.value] == index]

    #  sort the dataframes by `frame.timeEpoch`
    window_df.sort_values(
        by = FrameFields.frame_timeEpoch.value,
        axis = 0,
        ascending = True,
        inplace = True,
        na_position = 'last'
    )
    episode_df.sort_values(
        by = FrameFields.frame_timeEpoch.value,
        axis = 0,
        ascending = True,
        inplace = True,
        na_position = 'last'
    )

    # ***** helper functions *****

    def f__class_3_frames__count():
        """ Number of class 3 frames in the window """

        # filter:
        #   - packet subtype in `class_3_frames_list`
        _class_3_df = window_df[
            window_df[FrameFields.wlan_fc_typeSubtype.value].isin(class_3_frames_subtypes)
        ]
        return _class_3_df.shape[0]

    def f__class_3_frames__binary():
        """ Is class 3 frames count > 0 """
        return int(f__class_3_frames__count() > 0)

    def f__client_associated__binary():
        """ Is the client associated with an access point """
        return int(apAssociatedToClient(dataframe, the_client) is not None)

    def f__frames__arrival_rate():
        """ Number of frames originated at or transmitted by the client / window duration """

        # filter
        #   - either `source addr` or `transmitter addr` belongs to the client
        _client_df = window_df[
            (
                    (window_df[FrameFields.wlan_sa.value] == the_client) |
                    (window_df[FrameFields.wlan_ta.value] == the_client)
            )
        ]

        _, _, _window_duration = wp__window__time_epoch()
        _num_frames = _client_df.shape[0]

        # if no client associated frames are found in the window or window duration is 0, return np.NaN
        # NOTE: returning np.NaN and not 0, because metrics do not make sense if there are no client associated
        #       frames in the window or window duration is 0
        _arrival_rate = np.NaN
        if _num_frames >= 0 and _window_duration > 0:
            _arrival_rate = float(_num_frames) / float(_window_duration)
        return _arrival_rate

    def f__pspoll__count():
        """ Number of `ps_poll` frames in the window """

        # filter:
        #   - packet subtype == 0x1a
        _pspoll_frames = window_df[
            (window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.ps_poll.value)
        ]
        return _pspoll_frames.shape[0]

    def f__pspoll__binary():
        """ Is pspoll count > 0 """
        return int(f__pspoll__count() > 0)

    def f__pwrmgt_cycle__count():
        """ Number of cycles where cycle => frame with pwrmgt bit 1 then pwrmgt bit 0 """

        _num_cycles = 0
        _state = 0  # 0: begin, 1: bit = 1 found, 2: bit = 0 found; count++, goto state 0
        for idx, series in window_df.iterrows():
            _bit = series[FrameFields.wlan_fc_pwrmgt.value]
            if _bit is None:
                continue

            if _bit == 1 and _state == 0:
                _state = 1
            if _bit == 0 and _state == 1:
                _state = 2
            if _state == 2:
                _num_cycles += 1
                _state = 0

        return _num_cycles

    def f__pwrmgt_cycle__binary():
        """ Is pwrmgt cycle count > 0 """
        return int(f__pwrmgt_cycle__count() > 0)

    def f__rssi__slope():
        """ Slope of the line fitted through all points on rssi vs. time plot """

        _epoch_time_series = window_df[FrameFields.frame_timeEpoch.value]
        _epoch_time_series = _epoch_time_series.tolist()
        _rssi_series = window_df[FrameFields.radiotap_dbmAntsignal.value]
        _rssi_series = _rssi_series.tolist()

        _slope, _, _, _, _ = linregress(_epoch_time_series, _rssi_series)
        return _slope

    def f__ap_deauth_frames__count():
        """ Number of deauth frames directed towards the client """

        # filter:
        #   - packet type = `12` (deauth)
        #   - destination should be `the client`
        _ap_deauth_df = window_df[
            (
                    (window_df[
                         FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.deauthentication.value) &
                    (window_df[FrameFields.wlan_da.value] == the_client)
            )
        ]
        return _ap_deauth_df.shape[0]

    def f__ap_deauth_frames__binary():
        """ Is ap deauth frames count > 0 """
        return int(f__ap_deauth_frames__count() > 0)

    def f__max_consecutive_beacon_loss__count():
        """
        Maximum number of consecutive beacon frames that are not received according to a
        fixed time interval (assumed 105ms).
        """

        associated_ap_bssid = apAssociatedToClient(dataframe, the_client)
        _beacons_df = window_df[
            window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.beacon.value]
        if associated_ap_bssid is not None:
            _beacons_df = _beacons_df[
                (
                        (_beacons_df[FrameFields.wlan_bssid.value] == associated_ap_bssid) |
                        (_beacons_df[FrameFields.wlan_ta.value] == associated_ap_bssid)
                )
            ]

        # sort by `frame.time_epoch`
        _beacons_df.sort_values(
            by = FrameFields.frame_timeEpoch.value,
            axis = 0,
            ascending = True,
            inplace = True,
            na_position = 'last'
        )

        # max consecutive beacon loss count
        #   - defines maximum number of consecutive beacons lost in a window
        #   - consecutive == interval between packets < 105 milliseconds
        _max_consecutive_beacon_count = 0
        _beacon_interval_count = 0
        if _beacons_df.shape[0] > 1:
            _previous_epoch = float(_beacons_df.head(1)[FrameFields.frame_timeEpoch.value])
            _beacon_df = _beacons_df.iloc[1:]

            for _, frame in _beacon_df.iterrows():
                _current_epoch = float(frame[FrameFields.frame_timeEpoch.value])
                _delta_time = abs(_current_epoch - _previous_epoch)

                if _delta_time > 0.105:
                    _beacon_interval_count += 1
                else:
                    _beacon_interval_count = 0

                _max_consecutive_beacon_count = max(_max_consecutive_beacon_count, _beacon_interval_count)
                _previous_epoch = _current_epoch

        return _max_consecutive_beacon_count

    def f__max_consecutive_beacon_loss__binary():
        """ Is max consecutive beacon loss count > 7 """
        return int(f__max_consecutive_beacon_loss__count() > 7)

    def f__beacons_linear_slope__difference():
        """ """

        associated_ap_bssid = apAssociatedToClient(dataframe, the_client)
        _beacons_df = window_df[
            window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.beacon.value]
        if associated_ap_bssid is not None:
            _beacons_df = _beacons_df[
                (
                        (_beacons_df[FrameFields.wlan_bssid.value] == associated_ap_bssid) |
                        (_beacons_df[FrameFields.wlan_ta.value] == associated_ap_bssid)
                )
            ]

        # sort by `frame.time_epoch`
        _beacons_df.sort_values(
            by = FrameFields.frame_timeEpoch.value,
            axis = 0,
            ascending = True,
            inplace = True,
            na_position = 'last'
        )

        # if no beacons are found in the window, return 0
        # NOTE: returning 0 and not np.NaN, because it is understandable for a window to not have any beacons and
        #       its other metrics to still make sense
        if _beacons_df.shape[0] == 0:
            return 0

        _epoch_series = _beacons_df[FrameFields.frame_timeEpoch.value]
        _beacon_cdf = np.cumsum(np.ones(_epoch_series.shape[0]))

        # calculate local linear regression
        _local_trend = linregress(_epoch_series, _beacon_cdf)
        _global_trend = _local_trend

        if associated_ap_bssid is not None:
            try:
                # get global trend, if available
                _global_trend = ap_beacon_count_linear_trends[associated_ap_bssid]
            except KeyError:
                pass

        _g_slope, _, _, _, _ = _global_trend
        _l_slope, _, _, _, _ = _local_trend
        return abs(_g_slope - _l_slope)

    def f__null_frames__ratio():
        """ Number of null frames originating at the client / Number of frames originating at the client """

        # filter
        #   - `source addr` belongs to the client
        _client_df = window_df[
            (window_df[FrameFields.wlan_sa.value] == the_client)
        ]

        # filter:
        #   - source should be the client
        #   - packet type = `36` or `44` (null, qos null)
        _null_df = _client_df[
            (
                    (_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.null.value) |
                    (_client_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.qos_null.value)
            )
        ]

        # if no client associated frames are found in the window, return np.NaN
        # NOTE: returning np.NaN and not 0, because metrics do not make sense if there are no client associated
        #       frames in the window
        _null_count = np.NaN
        if _client_df.shape[0] > 0:
            _null_count = float(_null_df.shape[0]) / float(_client_df.shape[0])
        return _null_count

    def f__connection_frames__count():
        """
        Number of connection frames in the window
            - Association Response
            - Reassociation Response
        """

        # filter:
        #   - destination should be `the client`
        #   - packet type = `1` or `3` (association response, re-association response)
        _connection_df = window_df[
            (
                    (window_df[FrameFields.wlan_da.value] == the_client) &
                    (
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] ==
                             FrameSubtypes.association_response.value) |
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] ==
                             FrameSubtypes.reassociation_response.value)
                    )
            )
        ]
        return _connection_df.shape[0]

    def f__connection_frames__binary():
        """ Is connection frames count > 0 """
        return int(f__connection_frames__count() > 0)

    def f__frames__loss_ratio():
        """ Number of frames from client with retry bit 1 / Number of frames from client """

        # filter
        #   - either `source addr` or `transmitter addr` belongs to the client
        _client_df = window_df[
            (
                    (window_df[FrameFields.wlan_sa.value] == the_client) |
                    (window_df[FrameFields.wlan_ta.value] == the_client)
            )
        ]

        _df_retransmitted = _client_df[
            (_client_df[FrameFields.wlan_fc_retry.value] == 1)
        ]
        _num_retry = _df_retransmitted.shape[0]

        # if no client associated frames are found in the window, return np.NaN
        # NOTE: returning np.NaN and not 0, because metrics do not make sense if there are no client associated
        #       frames in the window
        _loss_rate = np.NaN
        if _client_df.shape[0] > 0:
            _loss_rate = float(_num_retry) / float(_client_df.shape[0])
        return _loss_rate

    def f__ack_to_data__ratio():
        """
        Number of acknowledgement frames from the client / Number of data frames from the client
            - ack + block_ack / data + qos_data
        """

        # filter
        #   - `source addr` belongs to the client
        #   - `type_subtype` is data/qos-data
        _data_df = window_df[
            (
                    (window_df[FrameFields.wlan_sa.value] == the_client) &
                    (
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.data.value) |
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.qos_data.value)
                    )
            )
        ]

        # filter
        #   - `source addr` belongs to the client
        #   - `type_subtype` is data/qos-data
        _ack_df = window_df[
            (
                    (window_df[FrameFields.wlan_da.value] == the_client) &
                    (
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.ack.value) |
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.block_ack.value)
                    )
            )
        ]

        _num_data = _data_df.shape[0]
        _num_ack = _ack_df.shape[0]

        # if no data frames are found in the window, return 0
        # NOTE: returning 0 and not np.NaN, because other metrics can still make sense if there are no data
        #       frames in the window
        _ratio = 0
        if _num_data > 0:
            _ratio = float(_num_ack) / float(_num_data)
        return _ratio

    def f__datarate__slope():
        """ Slope of the line fitted through all points on datarate vs. time plot """

        _epoch_time_series = window_df[FrameFields.frame_timeEpoch.value]
        _epoch_time_series = _epoch_time_series.tolist()
        _datarate_series = window_df[FrameFields.radiotap_datarate.value]
        _datarate_series = _datarate_series.tolist()

        _slope, _, _, _, _ = linregress(_epoch_time_series, _datarate_series)
        return _slope

    def f__rssi__mean():
        """ Mean of rssi values in the window """

        _rssi_series = window_df[FrameFields.radiotap_dbmAntsignal.value]
        return _rssi_series.mean()

    def f__rssi__sd():
        """ Standard Deviation of rssi values in the window """

        _rssi_series = window_df[FrameFields.radiotap_dbmAntsignal.value]
        return _rssi_series.std()

    def f__client_deauth_frames__count():
        """ Number of deauth frames originating from the client """

        # filter:
        #   - packet type = `12` (deauth)
        #   - source should be `the client`
        _client_deauth_df = window_df[
            (
                    (window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.deauthentication.value) &
                    (window_df[FrameFields.wlan_sa.value] == the_client)
            )
        ]
        return _client_deauth_df.shape[0]

    def f__beacons__count():
        """ Number of beacon frames from the associated ap in the window """

        associated_ap_bssid = apAssociatedToClient(dataframe, the_client)
        _beacons_df = window_df[
            window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.beacon.value]
        if associated_ap_bssid is not None:
            _beacons_df = _beacons_df[
                (
                        (_beacons_df[FrameFields.wlan_bssid.value] == associated_ap_bssid) |
                        (_beacons_df[FrameFields.wlan_ta.value] == associated_ap_bssid)
                )
            ]
        return _beacons_df.shape[0]

    def f__ack__count():
        """ Number of acknowledgement frames in the window """

        _ack_frames = window_df[
            (window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.ack.value)
        ]
        return _ack_frames.shape[0]

    def f__null_frames__count():
        """ Number of null frames in the window """

        # filter:
        #   - source should be in clients
        #   - power management bit = 0
        #   - packet type = `36` or `44` (null, qos null)
        _null_df = window_df[
            (
                    (window_df[FrameFields.wlan_sa.value] == the_client) &
                    (window_df[FrameFields.wlan_fc_pwrmgt.value] == 0) &
                    (
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.null.value) |
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] == FrameSubtypes.qos_null.value)
                    )
            )
        ]
        return _null_df.shape[0]

    def f__failure_assoc__count():
        """  """

        # filter:
        #   - `status code` != 0
        #   - destination should be `the client`
        #   - packet type = `1` or `3` (association response, re-association response)
        _assoc_reassoc_failure_response_df = window_df[
            (
                    (window_df[FrameFields.wlan_fixed_statusCode.value] != 0) &
                    (window_df[FrameFields.wlan_da.value] == the_client) &
                    (
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] ==
                             FrameSubtypes.association_response.value) |
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] ==
                             FrameSubtypes.reassociation_response.value)
                    )
            )
        ]
        return _assoc_reassoc_failure_response_df.shape[0]

    def f__success_assoc_count():
        """ """

        # filter:
        #   - `status code` = 0
        #   - destination should be `the client`
        #   - packet type = `1` or `3` (association response, re-association response)
        _assoc_reassoc_success_response_df = window_df[
            (
                    (window_df[FrameFields.wlan_fixed_statusCode.value] == 0) &
                    (window_df[FrameFields.wlan_da.value] == the_client) &
                    (
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] ==
                             FrameSubtypes.association_response.value) |
                            (window_df[FrameFields.wlan_fc_typeSubtype.value] ==
                             FrameSubtypes.reassociation_response.value)
                    )
            )
        ]
        return _assoc_reassoc_success_response_df.shape[0]

    def wp__window__time_epoch():
        """
        1. Window start epoch time.
        2. Window end epoch time.
        3. Window duration.
        """

        _window_start_epoch = float(window_df.head(1)[FrameFields.frame_timeEpoch.value])
        _window_end_epoch = float((window_df.tail(1))[FrameFields.frame_timeEpoch.value])
        _window_duration = float(_window_end_epoch - _window_start_epoch)
        _window_duration = abs(_window_duration)
        return _window_start_epoch, _window_end_epoch, _window_duration

    f__output = dict()

    if WindowMetrics.class_3_frames__count in required_features:
        f__output[WindowMetrics.class_3_frames__count] = f__class_3_frames__count()

    if WindowMetrics.class_3_frames__binary in required_features:
        f__output[WindowMetrics.class_3_frames__binary] = f__class_3_frames__binary()

    if WindowMetrics.client_associated__binary in required_features:
        f__output[WindowMetrics.client_associated__binary] = f__client_associated__binary()

    if WindowMetrics.frames__arrival_rate in required_features:
        f__output[WindowMetrics.frames__arrival_rate] = f__frames__arrival_rate()

    if WindowMetrics.pspoll__count in required_features:
        f__output[WindowMetrics.pspoll__count] = f__pspoll__count()

    if WindowMetrics.pspoll__binary in required_features:
        f__output[WindowMetrics.pspoll__binary] = f__pspoll__binary()

    if WindowMetrics.pwrmgt_cycle__count in required_features:
        f__output[WindowMetrics.pwrmgt_cycle__count] = f__pwrmgt_cycle__count()

    if WindowMetrics.pwrmgt_cycle__binary in required_features:
        f__output[WindowMetrics.pwrmgt_cycle__binary] = f__pwrmgt_cycle__binary()

    if WindowMetrics.rssi__slope in required_features:
        f__output[WindowMetrics.rssi__slope] = f__rssi__slope()

    if WindowMetrics.ap_deauth_frames__count in required_features:
        f__output[WindowMetrics.ap_deauth_frames__count] = f__ap_deauth_frames__count()

    if WindowMetrics.ap_deauth_frames__binary in required_features:
        f__output[WindowMetrics.ap_deauth_frames__binary] = f__ap_deauth_frames__binary()

    if WindowMetrics.max_consecutive_beacon_loss__count in required_features:
        f__output[WindowMetrics.max_consecutive_beacon_loss__count] = f__max_consecutive_beacon_loss__count()

    if WindowMetrics.max_consecutive_beacon_loss__binary in required_features:
        f__output[WindowMetrics.max_consecutive_beacon_loss__binary] = f__max_consecutive_beacon_loss__binary()

    if WindowMetrics.beacons_linear_slope__difference in required_features:
        f__output[WindowMetrics.beacons_linear_slope__difference] = f__beacons_linear_slope__difference()

    if WindowMetrics.null_frames__ratio in required_features:
        f__output[WindowMetrics.null_frames__ratio] = f__null_frames__ratio()

    if WindowMetrics.connection_frames__count in required_features:
        f__output[WindowMetrics.connection_frames__count] = f__connection_frames__count()

    if WindowMetrics.connection_frames__binary in required_features:
        f__output[WindowMetrics.connection_frames__binary] = f__connection_frames__binary()

    if WindowMetrics.frames__loss_ratio in required_features:
        f__output[WindowMetrics.frames__loss_ratio] = f__frames__loss_ratio()

    if WindowMetrics.ack_to_data__ratio in required_features:
        f__output[WindowMetrics.ack_to_data__ratio] = f__ack_to_data__ratio()

    if WindowMetrics.datarate__slope in required_features:
        f__output[WindowMetrics.datarate__slope] = f__datarate__slope()

    if WindowMetrics.rssi__mean in required_features:
        f__output[WindowMetrics.rssi__mean] = f__rssi__mean()

    if WindowMetrics.rssi__sd in required_features:
        f__output[WindowMetrics.rssi__sd] = f__rssi__sd()

    if WindowMetrics.client_deauth_frames__count in required_features:
        f__output[WindowMetrics.client_deauth_frames__count] = f__client_deauth_frames__count()

    if WindowMetrics.beacons__count in required_features:
        f__output[WindowMetrics.beacons__count] = f__beacons__count()

    if WindowMetrics.ack__count in required_features:
        f__output[WindowMetrics.ack__count] = f__ack__count()

    if WindowMetrics.null_frames__count in required_features:
        f__output[WindowMetrics.null_frames__count] = f__null_frames__count()

    if WindowMetrics.failure_assoc__count in required_features:
        f__output[WindowMetrics.failure_assoc__count] = f__failure_assoc__count()

    if WindowMetrics.success_assoc__count in required_features:
        f__output[WindowMetrics.success_assoc__count] = f__success_assoc_count()

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


def envSetup(source_dir, destination_dir):
    aux.createDirectoryIfRequired(source_dir)
    aux.createDirectoryIfRequired(destination_dir)

    if aux.isDirectoryEmpty(source_dir):
        raise FileNotFoundError("No [csv] files to process")
    if not aux.isDirectoryEmpty(destination_dir):
        raise FileExistsError("Please clear the contents of `{:s}` to prevent any overwrites".format(
            path.basename(destination_dir)
        ))


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

    print('\t', '•• Dataframe shape (on read):', csv_dataframe.shape)

    # sanitize data
    #   - drop unnecessary columns
    csv_dataframe.drop(columns = ['radiotap.dbm_antsignal_2', ], inplace = True)
    #   - drop not available values
    csv_dataframe.dropna(axis = 0, subset = [
        FrameFields.frame_timeEpoch.value,
        FrameFields.radiotap_dbmAntsignal.value,
        FrameFields.radiotap_datarate.value,
    ], inplace = True)

    print('\t', '•• Dataframe shape (after dropping null values):', csv_dataframe.shape)

    #   - optimize memory usage
    csv_dataframe[FrameFields.frame_timeEpoch.value] = csv_dataframe[FrameFields.frame_timeEpoch.value].astype(float)
    csv_dataframe[FrameFields.wlan_bssid.value] = csv_dataframe[FrameFields.wlan_bssid.value].astype('category')
    csv_dataframe[FrameFields.wlan_sa.value] = csv_dataframe[FrameFields.wlan_sa.value].astype('category')
    csv_dataframe[FrameFields.wlan_da.value] = csv_dataframe[FrameFields.wlan_da.value].astype('category')
    csv_dataframe[FrameFields.wlan_ta.value] = csv_dataframe[FrameFields.wlan_ta.value].astype('category')
    csv_dataframe[FrameFields.wlan_ra.value] = csv_dataframe[FrameFields.wlan_ra.value].astype('category')
    csv_dataframe[FrameFields.wlan_fixed_statusCode.value] = \
        csv_dataframe[FrameFields.wlan_fixed_statusCode.value].astype('category')
    csv_dataframe[FrameFields.wlan_ssid.value] = csv_dataframe[FrameFields.wlan_ssid.value].astype('category')
    csv_dataframe[FrameFields.wlan_fc_typeSubtype.value] = \
        csv_dataframe[FrameFields.wlan_fc_typeSubtype.value].astype('category')
    csv_dataframe[FrameFields.wlan_fc_retry.value] = csv_dataframe[FrameFields.wlan_fc_retry.value].astype('category')
    csv_dataframe[FrameFields.wlan_fc_pwrmgt.value] = csv_dataframe[FrameFields.wlan_fc_pwrmgt.value].astype('category')
    csv_dataframe[FrameFields.radiotap_datarate.value] = \
        csv_dataframe[FrameFields.radiotap_datarate.value].astype(float, errors = 'ignore')
    csv_dataframe[FrameFields.radiotap_dbmAntsignal.value] = \
        csv_dataframe[FrameFields.radiotap_dbmAntsignal.value].astype(float, errors = 'ignore')

    # sort the dataframe by `frame.timeEpoch`
    csv_dataframe.sort_values(
        by = FrameFields.frame_timeEpoch.value,
        axis = 0,
        ascending = True,
        inplace = True,
        na_position = 'last'
    )
    return csv_dataframe


def csv2records(
        source_dir, destination_dir, csv_filename: str, access_points, clients, assign_rbs_tags = False,
        separate_client_files = False
):
    """ Processes a given frame csv file to generate episode characteristics """

    # current time
    timestamp = datetime.datetime.now()

    # read csv file
    csv_filepath = path.join(source_dir, csv_filename)
    main_dataframe = readCsvFile(csv_filepath)
    csv_file__uuid = timestamp.strftime('%d%m%Y%H%M%S') + '.' + str(uuid4())
    print('• UUID generated for the file {:s}: {:s}'.format(csv_filename, csv_file__uuid))

    if clients is None:
        clients = allClientsIn(main_dataframe)

    # output column orders
    # semi_processed_output_column_order = main_dataframe.columns.values.tolist()
    # semi_processed_output_column_order.sort()
    # semi_processed_output_column_order.append(EpisodeProperties.episode__id.value)
    # semi_processed_output_column_order.append(EpisodeProperties.associated_client__mac.value)
    # semi_processed_output_column_order.append(EpisodeProperties.csv_file__uuid.value)

    processed_output_column_order = csvColumnNames(MLFeatures)
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

    # all episodes characteristics as list of 2-tuples
    #   - 1. features
    #   - 2. properties
    window_characteristics_list = list()

    # ### Processing ###
    # 1. keep only relevant frames in memory
    main_dataframe = relevanceFilter(main_dataframe, clients, access_points)
    print('• Dataframe shape (relevance filter):', main_dataframe.shape)

    # 1.1 calculate linear trends for all access points in the main dataframe
    existing_access_points = allAccessPointsIn(main_dataframe)
    ap_beacon_count_linear_trends = defineLinearTrendForBeacons(main_dataframe, existing_access_points)

    # 2. for each client...
    for the_client in clients:
        # 2.a. copy the main_dataframe
        dataframe = main_dataframe.copy(deep = True)

        # 2.b. filter frames belonging to the client
        dataframe = filterByMacAddress(dataframe, the_client)
        if dataframe is None:
            print('\t', '•• No relevant frames found for client {:s}'.format(the_client))
            continue

        # 2.c. define episodes on frames
        print('• Creating episodes and window boundaries from the frames for client: {:s}'.format(the_client))
        result = defineEpisodeAndWindowBoundaries(dataframe)
        if result is not None:
            dataframe, count, indexes = result
            print('\t', '•• Windows generated for client {:s} -'.format(the_client), count)
            if count == 0:
                continue
        else:
            print('\t', '•• Windows generated for client {:s} -'.format(the_client), 0)
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
        for idx in indexes:
            # 2.d.1. get all frames belonging to the episode/window
            _df = dataframe[
                (dataframe[WindowProperties.window__id.value] == idx) |
                (dataframe[EpisodeProperties.episode__id.value] == idx)
                ]
            # 2.d.2. sort the dataframe by `frame.time_epoch`
            _df.sort_values(
                by = FrameFields.frame_timeEpoch.value,
                axis = 0,
                ascending = True,
                inplace = True,
                na_position = 'last'
            )

            # 2.d.3. compute episode characteristics
            window_features = computeFeaturesAndProperties(
                _df, the_client, idx,
                ap_beacon_count_linear_trends,
                # MLFeatures
                WindowMetrics.asList()
            )

            # 2.d.4. append to output
            window_characteristics_list.append(window_features)

    # 3. make a dataframe from window characteristics
    window_characteristics_df = windowCharacteristicsAsDataframe(
        window_characteristics_list,
        MLFeatures
    )
    print('• Total windows generated: {:d}'.format(len(window_characteristics_df)))
    # 3.a. drop null values, since ML model can't make any sense of this
    window_characteristics_df.dropna(
        axis = 0,
        inplace = True,
    )
    print('• Total windows generated (after dropping null values): {:d}'.format(len(window_characteristics_df)))

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
    window_characteristics_df.to_csv(
        output_csvfile, sep = ',', index = False, header = True,
        columns = processed_output_column_order
    )


# *****************************************************************************
# *****************************************************************************

if __name__ == '__main__':
    __source_dir = DefaultDirectory["data_csv"]
    __destination_dir = DefaultDirectory["data_records"]

    __access_points = [

    ]

    __clients = [

    ]

    envSetup(__source_dir, __destination_dir)
    csv_filenames = aux.selectFiles(__source_dir, csv_extensions)
    for idx, filename in enumerate(csv_filenames):
        print('Started processing file: {:s}'.format(filename))
        csv2records(
            source_dir = __source_dir,
            destination_dir = __destination_dir,
            csv_filename = filename,
            access_points = __access_points,
            clients = __clients,
            assign_rbs_tags = False,
            separate_client_files = False,
        )
        print('-' * 40)
        print()
    pass
