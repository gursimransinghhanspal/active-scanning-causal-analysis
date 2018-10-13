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

from globals import ASCause, FeaturesForCause, ProjectDirectory
from src.aux import createDirectoryIfRequired, isDirectoryEmpty

__label_self = 0
__label_rest = 1

RecordForCause = {
    ASCause.apsp: path.join(ProjectDirectory["data.records_merged"], "apsp_mergedRecord.csv"),
    ASCause.bl: path.join(ProjectDirectory["data.records_merged"], "bl_mergedRecord.csv"),
    ASCause.ce: path.join(ProjectDirectory["data.records_merged"], "ce_mergedRecord.csv"),
    ASCause.lrssi: path.join(ProjectDirectory["data.records_merged"], "lrssi_mergedRecord.csv"),
    ASCause.pscanA: path.join(ProjectDirectory["data.records_merged"], "pscanA_mergedRecord.csv"),
    ASCause.pscanU: path.join(ProjectDirectory["data.records_merged"], "pscanU_mergedRecord.csv"),
    # ASCause.pwr: path.join(ProjectDirectory["data.records_merged"], "pwr_mergedRecord.csv"),
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
    return records_dataframe[fields]


def labelOne():
    pass


def labelAll():
    pass


def labelOneVsAll(record_for_cause: dict, destination_dir, features_for_cause):
    """ """

    # get name of each feature
    def featureNames(features):
        return [name.value for name in features]

    causes = ASCause.asSet()
    for the_cause in causes:
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
        #
        self_X = np.asarray(self_df)
        rest_X = np.asarray(rest_df)
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


if __name__ == '__main__':
    __destination_dir = ProjectDirectory["data.ml_labeled"]

    envSetup(__destination_dir)
    labelOneVsAll(
        record_for_cause = RecordForCause,
        destination_dir = __destination_dir,
        features_for_cause = FeaturesForCause.copy()
    )
    pass
