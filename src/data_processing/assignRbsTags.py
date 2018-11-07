# def assignRuleBasedTags(episodes_df: pd.DataFrame):
#     """
#     Assigns a 'cause' field to each row of the dataframe with tags for each cause inferred
#     by the rule based checks.
#     """
#
#     def __low_rssi(episode):
#         """
#         For every episode, calculate `mean` and `standard deviation` for rssi v.
#         check: `mean` < -72dB and `std dev` > 12dB
#         """
#
#         if episode[WindowMetrics.rssi__mean.v] < -72 and episode[WindowMetrics.rssi__sd.v] > 12:
#             return True
#         return False
#
#     def __data_frame_loss(episode):
#         """
#         use `fc.retry` field
#         check: #(fc.retry == 1)/#(fc.retry == 1 || fc.retry == 0) > 0.5
#         """
#
#         if episode[WindowMetrics.frame__loss_rate.v] > 0.5:
#             return True
#         return False
#
#     def __power_state_low_to_high_v1(episode):
#         """
#         calculate number of frames per second.
#         check: if #fps > 2
#         """
#
#         _frame_frequency = episode[WindowMetrics.frames__arrival_rate.v]
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
#         _frame_frequency = episode[WindowMetrics.frames__arrival_rate.v]
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
#         if episode[WindowMetrics.ap_deauth_frames__count.v] > 0:
#             return True
#         return False
#
#     def __client_deauth(episode):
#         """
#         check for deauth packet from client
#         deauth: fc.type_subtype == 12
#         """
#
#         if episode[WindowMetrics.client_deauth_frames__count.v] > 0:
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
#         if (episode[WindowMetrics.beacons__count.v] == 0 or
#                 episode[WindowMetrics.max_consecutive_beacon_loss__count.v] >= 8 or
#                 (episode[WindowMetrics.ack__count.v] == 0 and episode[WindowMetrics.null_frames__count.v] >
#  0)):
#             return True
#         return False
#
#     def __unsuccessful_assoc_auth_reassoc_deauth(episode):
#         if (episode[WindowMetrics.ap_deauth_frames__count.v] > 0 and episode[
#             WindowMetrics.failure_assoc__count.v] == 0):
#             return True
#         return False
#
#     def __successful_assoc_auth_reassoc_deauth(episode):
#         if episode[WindowMetrics.ap_deauth_frames__count.v] == 0 and \
#                 episode[WindowMetrics.success_assoc__count.v] > 0:
#             return True
#         return False
#
#     def __class_3_frames(episode):
#         if episode[WindowMetrics.class_3_frames__count.v] > 0:
#             return True
#         return False
#
#     for idx, _episode in episodes_df.iterrows():
#
#         cause_str = ''
#         if __low_rssi(_episode):
#             cause_str += RBSCauses.low_rssi.v
#
#         if __data_frame_loss(_episode):
#             cause_str += RBSCauses.data_frame_loss.v
#
#         if __power_state_low_to_high_v1(_episode):
#             cause_str += RBSCauses.power_state.v
#
#         if __power_state_low_to_high_v2(_episode):
#             cause_str += RBSCauses.power_state_v2.v
#
#         if __ap_deauth(_episode):
#             cause_str += RBSCauses.ap_side_procedure.v
#
#         if __client_deauth(_episode):
#             cause_str += RBSCauses.client_deauth.v
#
#         if __beacon_loss(_episode):
#             cause_str += RBSCauses.beacon_loss.v
#
#         if __unsuccessful_assoc_auth_reassoc_deauth(_episode):
#             cause_str += RBSCauses.unsuccessful_association.v
#
#         if __successful_assoc_auth_reassoc_deauth(_episode):
#             cause_str += RBSCauses.successful_association.v
#
#         if __class_3_frames(_episode):
#             cause_str += RBSCauses.class_3_frames.v
#
#         episodes_df.loc[idx, 'rbs__cause_tags'] = cause_str
#     return episodes_df
