#!python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# Preprocessor
# |- merge_records.py
#       := Merge all the records in one file
#
#
from os import path, walk

import pandas as pd

from aux import createDirectoryIfRequired
from globals import ProjectDirectory, Features, csv_extensions, RecordProperties
from src.aux import selectFilesByExtension


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
    # records_dataframe[WindowMetrics.rssi__mean.value] = records_dataframe[WindowMetrics.rssi__mean.value].fillna(0)
    # records_dataframe[WindowMetrics.rssi__stddev.value] = records_dataframe[WindowMetrics.rssi__stddev.value].fillna(0)
    # records_dataframe[WindowMetrics.rssi__linslope.value] = records_dataframe[WindowMetrics.rssi__linslope.value].fillna(0)
    # records_dataframe[WindowMetrics.non_empty_data_frames__rate.value] = records_dataframe[
    # WindowMetrics.non_empty_data_frames__rate.value].fillna(-1)
    # records_dataframe[WindowMetrics.empty_null_frames__rate.value] = records_dataframe[WindowMetrics.empty_null_frames__rate.value].fillna(-1)
    # records_dataframe[WindowMetrics.awake_null_frames__rate.value] = records_dataframe[WindowMetrics.awake_null_frames__rate.value].fillna(-1)
    # records_dataframe.dropna(inplace = True)
    return records_dataframe[fields]


def mergeRecords(source_dir, destination_filepath, fields):
    """ """

    file_df = pd.DataFrame(columns = fields)
    file_df.to_csv(destination_filepath, mode = 'w', sep = '|', index = False, header = True, columns = fields)

    for src_dir, _, all_files in walk(source_dir):
        print("Processing directory", path.basename(src_dir))

        for csv_filename in selectFilesByExtension(src_dir, all_files, csv_extensions):
            file_df = readRecordsFile(path.join(src_dir, csv_filename), fields)
            #
            # for `apsp` only, choose only episodes with Features.ap_disconnection_frames__binary as 1
            # TODO: comment out for all other causes
            # file_df = file_df[file_df[Features.ap_disconnection_frames__binary.v] == 1]
            #
            file_df.to_csv(destination_filepath, mode = 'a', sep = '|', index = False, header = False, columns = fields)
            print(file_df.shape[0])
        print()


if __name__ == '__main__':
    __source_dir = path.join(ProjectDirectory["data.record"], "pwr")
    __destination_dir = path.join(ProjectDirectory["data.records_merged"])

    createDirectoryIfRequired(__destination_dir)

    mergeRecords(
        source_dir = __source_dir,
        destination_filepath = path.join(__destination_dir, "pwr" + "_mergedRecord.csv"),
        fields = Features.valuesAsList() + RecordProperties.valuesAsList()
    )
