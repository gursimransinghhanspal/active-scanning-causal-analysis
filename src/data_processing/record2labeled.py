#!python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# Preprocessor
# |- records2labeled.py
#       := Choose the features from `records` files and create a merged labeled dataset for machine learning
#
#

from os import path

import numpy as np
import pandas as pd
from sklearn.utils import shuffle

from globals import ASCause, Features, ProjectDirectory, RecordProperties, MLFeaturesForCause
from src.aux import createDirectoryIfRequired, isDirectoryEmpty

__label_self = 1
__label_rest = 0

required_features = [
    Features.rssi__mean,
    Features.rssi__stddev,
    Features.rssi__linslope,
    Features.non_empty_data_frames__rate,
    Features.sleep_frames__binary,
    Features.empty_null_frames__rate,
    Features.directed_probe_requests__binary,
    Features.broadcasted_probe_requests__binary,
    # Features.beacon_loss__count,
    Features.awake_null_frames__rate,
    Features.sleep_null_frames__rate,
    Features.ap_disconnection_frames__binary,
    Features.client_disconnection_frames__binary,
    Features.client_associated__binary,
    Features.client_connection_request_frames__binary_3,
    Features.client_connection_response_frames__binary_3,
    Features.client_connection_success_response_frames__binary_3,
]
required_feature_values = [
    i.v for i in required_features
]

RecordForCause = {
    ASCause.apsp  : path.join(ProjectDirectory["data.records_merged"], "apsp_mergedRecord.csv"),
    ASCause.bl    : path.join(ProjectDirectory["data.records_merged"], "bl_mergedRecord.csv"),
    ASCause.ce    : path.join(ProjectDirectory["data.records_merged"], "ce_mergedRecord.csv"),
    ASCause.lrssi : path.join(ProjectDirectory["data.records_merged"], "lrssi_mergedRecord.csv"),
    ASCause.pscanA: path.join(ProjectDirectory["data.records_merged"], "pscan-a_mergedRecord.csv"),
    ASCause.pscanU: path.join(ProjectDirectory["data.records_merged"], "pscan-u_mergedRecord.csv"),
    ASCause.pwr   : path.join(ProjectDirectory["data.records_merged"], "pwr_mergedRecord.csv"),
}


def envSetup(destination_dir):
    createDirectoryIfRequired(destination_dir)

    if not isDirectoryEmpty(destination_dir):
        raise FileExistsError("Please clear the contents of `{:s}` to prevent any overwrites".format(
            path.basename(destination_dir)
        ))


def readRecordsFile(filepath, fields):
    """ """

    records_dataframe = pd.read_csv(
        filepath_or_buffer = filepath,
        sep = '|',  # comma separated values (default)
        header = 0,  # use first row as column_names
        index_col = None,  # do not use any column to index
        skipinitialspace = True,  # skip any space after delimiter
        na_values = ['', ],  # values to consider as `not available`
        na_filter = True,  # detect `not available` values
        skip_blank_lines = True,  # skip any blank lines in the file
        float_precision = 'high',
        usecols = fields,  # read only the required fields
        error_bad_lines = True,
        warn_bad_lines = True
    )
    # re-order the columns
    records_dataframe.fillna(0, inplace = True)
    return records_dataframe[fields]


def labelAll(record_for_cause: dict, destination_dir):
    #
    all_columns = Features.valuesAsList() + RecordProperties.valuesAsList()
    #
    df_apsp = readRecordsFile(record_for_cause[ASCause.apsp], all_columns)
    df_bl = readRecordsFile(record_for_cause[ASCause.bl], all_columns)
    df_ce = readRecordsFile(record_for_cause[ASCause.ce], all_columns)
    df_lrssi = readRecordsFile(record_for_cause[ASCause.lrssi], all_columns)
    df_pscanA = readRecordsFile(record_for_cause[ASCause.pscanA], all_columns)
    df_pscanU = readRecordsFile(record_for_cause[ASCause.pscanU], all_columns)
    df_pwr = readRecordsFile(record_for_cause[ASCause.pwr], all_columns)
    #
    print("Shapes:")
    print("apsp:", df_apsp.shape)
    print("bl:", df_bl.shape)
    print("ce:", df_ce.shape)
    print("lrssi:", df_lrssi.shape)
    print("pscan-a:", df_pscanA.shape)
    print("pscan-u:", df_pscanU.shape)
    print("pwr:", df_pwr.shape)
    #
    tl = 'trainingLabel'
    df_apsp[tl] = 0
    df_bl[tl] = 1
    df_ce[tl] = 2
    df_lrssi[tl] = 3
    df_pscanA[tl] = 4
    df_pscanU[tl] = 5
    df_pwr[tl] = 6
    #
    # sample_sz = min(
    #     df_apsp.shape[0],
    #     df_bl.shape[0],
    #     df_ce.shape[0],
    #     df_lrssi.shape[0],
    #     df_pscanA.shape[0],
    #     df_pscanU.shape[0],
    #     df_pwr.shape[0]
    # )
    # print("Sample Size:", sample_sz)
    # #
    # df_apsp = df_apsp.sample(sample_sz)
    # df_bl = df_bl.sample(sample_sz)
    # df_ce = df_ce.sample(sample_sz)
    # df_lrssi = df_lrssi.sample(sample_sz)
    # df_pscanA = df_pscanA.sample(sample_sz)
    # df_pscanU = df_pscanU.sample(sample_sz)
    # df_pwr = df_pwr.sample(sample_sz)
    #
    df = pd.concat((df_apsp, df_bl, df_ce, df_lrssi, df_pscanA, df_pscanU, df_pwr))
    df = shuffle(df).reset_index(drop = True)
    #
    X = np.asarray(df[required_feature_values])
    y = np.asarray(df[tl])
    #
    np.save(path.join(destination_dir, "fullFeatureSet_unsampled_featureMatrix.npy"), X)
    np.save(path.join(destination_dir, "fullFeatureSet_unsampled_targetVector.npy"), y)
    #
    df.to_csv(
        path.join(destination_dir, "fullFeatureSet_unsampled_dataframe.csv"),
        sep = '|',
        header = True,
        index = False,
    )


def labelOneVsAll(record_for_cause: dict, destination_dir, features_for_cause):
    """ """

    #
    all_columns = Features.valuesAsList() + RecordProperties.valuesAsList()

    # get name of each feature
    def featureValues(features):
        return [name.value for name in features]

    causes = ASCause.asSet()
    for the_cause in causes:
        print(the_cause)
        feature_values_for_cause = featureValues(features_for_cause[the_cause])
        #
        self_df = readRecordsFile(record_for_cause[the_cause], all_columns)
        #
        rest_causes = causes.difference({the_cause, })
        rest_df = pd.DataFrame(columns = feature_values_for_cause)
        for _cause in rest_causes:
            _cause_df = readRecordsFile(record_for_cause[_cause], all_columns)
            rest_df = pd.concat([rest_df, _cause_df], axis = 0, ignore_index = True, sort = False)
            pass
        #
        tl = 'trainingLabel'
        self_df[tl] = 1
        rest_df[tl] = 0
        #
        print("Shapes:")
        print("self:", self_df.shape)
        print("rest:", rest_df.shape)
        #
        # sample_sz = min(self_df.shape[0], rest_df.shape[0])
        # print("Sample Size:", sample_sz)
        # #
        # self_df = self_df.sample(sample_sz)
        # rest_df = rest_df.sample(sample_sz)
        #
        df = pd.concat((self_df, rest_df), sort = False)
        df = shuffle(df)
        #
        X = np.asarray(df[feature_values_for_cause])
        y = np.asarray(df[tl])
        #
        np.save(path.join(destination_dir, "selectedFeatureSet_unsampled_" + the_cause.name + "_featureMatrix.npy"), X)
        np.save(path.join(destination_dir, "selectedFeatureSet_unsampled_" + the_cause.name + "_targetVector.npy"), y)
        #
        df.to_csv(
            path.join(destination_dir, "selectedFeatureSet_unsampled_" + the_cause.name + "_dataframe.csv"),
            sep = '|',
            header = True,
            index = False,
        )
        print()


if __name__ == '__main__':
    __destination_dir = ProjectDirectory["data.ml_labeled"]

    # envSetup(__destination_dir)
    # labelOneVsAll(
    #     record_for_cause = RecordForCause,
    #     destination_dir = __destination_dir,
    #     features_for_cause = MLFeaturesForCause.copy()
    # )
    labelAll(
        record_for_cause = RecordForCause,
        destination_dir = __destination_dir,
    )
    pass
