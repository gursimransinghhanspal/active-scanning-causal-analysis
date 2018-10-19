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

from globals import ASCause, MLFeaturesForCause, ProjectDirectory, WindowMetrics
from src.aux import createDirectoryIfRequired, isDirectoryEmpty

__label_self = 0
__label_rest = 1

RecordForCause = {
    ASCause.apsp  : path.join(ProjectDirectory["data.records_merged"], "apsp_mergedRecord.csv"),
    ASCause.bl    : path.join(ProjectDirectory["data.records_merged"], "bl_mergedRecord.csv"),
    ASCause.ce    : path.join(ProjectDirectory["data.records_merged"], "ce_mergedRecord.csv"),
    ASCause.lrssi : path.join(ProjectDirectory["data.records_merged"], "lrssi_mergedRecord.csv"),
    ASCause.pscanA: path.join(ProjectDirectory["data.records_merged"], "pscan_a_mergedRecord.csv"),
    ASCause.pscanU: path.join(ProjectDirectory["data.records_merged"], "pscan_u_mergedRecord.csv"),
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
        sep = ',',  # comma separated values (default)
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
    records_dataframe.dropna(inplace = True)
    return records_dataframe[fields]


def labelOne():
    pass


def labelAll(record_for_cause: dict, destination_dir):

    #
    df_apsp = readRecordsFile(record_for_cause[ASCause.apsp], WindowMetrics.valuesAsList())
    df_bl = readRecordsFile(record_for_cause[ASCause.bl], WindowMetrics.valuesAsList())
    df_ce = readRecordsFile(record_for_cause[ASCause.ce], WindowMetrics.valuesAsList())
    df_lrssi = readRecordsFile(record_for_cause[ASCause.lrssi], WindowMetrics.valuesAsList())
    df_pscanA = readRecordsFile(record_for_cause[ASCause.pscanA], WindowMetrics.valuesAsList())
    df_pscanU = readRecordsFile(record_for_cause[ASCause.pscanU], WindowMetrics.valuesAsList())
    df_pwr = readRecordsFile(record_for_cause[ASCause.pwr], WindowMetrics.valuesAsList())
    #
    df_apsp['trainingLabel'] = 0
    df_bl['trainingLabel'] = 1
    df_ce['trainingLabel'] = 2
    df_lrssi['trainingLabel'] = 3
    df_pscanA['trainingLabel'] = 4
    df_pscanU['trainingLabel'] = 5
    df_pwr['trainingLabel'] = 6
    #
    # sample_sz = min(df_apsp.shape[0], rest_df.shape[0])
    # print(sample_sz)
    # self_sample = np.random.choice(list(range(self_df.shape[0])), sample_sz, replace = False)
    # rest_sample = np.random.choice(list(range(rest_df.shape[0])), sample_sz, replace = False)
    # self_df = self_df.loc[self_sample, :]
    # rest_df = rest_df.loc[rest_sample, :]
    #
    df = pd.concat((df_apsp, df_bl, df_ce, df_lrssi, df_pscanA, df_pscanU, df_pwr))
    X = np.asarray(df[WindowMetrics.valuesAsList()])
    y = np.asarray(df['trainingLabel'])
    #
    #
    # print(feature_matrix)
    # print(target_vector)
    #
    np.save(path.join(destination_dir, "All_featureMatrix.npy"), X)
    np.save(path.join(destination_dir, "All_targetVector.npy"), y)
    #
    df.to_csv(
        path.join(destination_dir, "All_featureMatrix.csv"),
        sep = ',',
        header = True,
        index = False,
    )


def labelOneVsAll(record_for_cause: dict, destination_dir, features_for_cause):
    """ """

    # get name of each feature
    def featureNames(features):
        return [name.value for name in features]

    causes = ASCause.asSet()
    for the_cause in causes:
        print(the_cause)
        feature_names = featureNames(features_for_cause[the_cause])
        #
        self_df = readRecordsFile(record_for_cause[the_cause], feature_names)
        #
        rest_causes = causes.difference({the_cause, })
        rest_df = pd.DataFrame(columns = feature_names)
        for _cause in rest_causes:
            _cause_df = readRecordsFile(record_for_cause[_cause], feature_names)
            rest_df = pd.concat([rest_df, _cause_df], axis = 0, ignore_index = True)
            pass

        sample_sz = min(self_df.shape[0], rest_df.shape[0])
        print(sample_sz)
        self_sample = np.random.choice(list(range(self_df.shape[0])), sample_sz, replace = False)
        rest_sample = np.random.choice(list(range(rest_df.shape[0])), sample_sz, replace = False)
        self_df = self_df.loc[self_sample, :]
        rest_df = rest_df.loc[rest_sample, :]
        #
        self_X = np.asarray(self_df)
        rest_X = np.asarray(rest_df)
        #
        #
        self_y = np.ones((self_X.shape[0],))
        rest_y = np.zeros((rest_X.shape[0],))
        #
        feature_matrix = np.vstack([self_X, rest_X])
        target_vector = np.hstack([self_y, rest_y])
        # print(feature_matrix)
        # print(target_vector)
        #
        np.save(path.join(destination_dir, "{:s}_OneVsAll_featureMatrix.npy".format(the_cause.name)), feature_matrix)
        np.save(path.join(destination_dir, "{:s}_OneVsAll_targetVector.npy".format(the_cause.name)), target_vector)
        #
        self_df['trainingLabel'] = 1
        rest_df['trainingLabel'] = 0
        out_df: pd.DataFrame = pd.concat((self_df, rest_df))
        out_df.to_csv(
            path.join(destination_dir, "{:s}_OneVsAll_featureMatrix.csv".format(the_cause.name)),
            sep = ',',
            header = True,
            index = False,
        )


if __name__ == '__main__':
    __destination_dir = ProjectDirectory["data.ml_labeled"]

    envSetup(__destination_dir)
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
