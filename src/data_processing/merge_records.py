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
from os import path

import pandas as pd

from globals import MLFeatures, csv_extensions, ProjectDirectory
from src.aux import selectFiles


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


def mergeRecords(source_dir, destination_filepath):
    """ """

    record_filenames = selectFiles(source_dir, csv_extensions)
    record_fields = [item.value for item in MLFeatures]
    for filename in record_filenames:
        file_df = readRecordsFile(path.join(source_dir, filename), record_fields)
        file_df.to_csv(destination_filepath, mode = 'a', sep = ',', index = False, header = True,
                       columns = record_fields)


if __name__ == '__main__':
    __source_dir = path.join(ProjectDirectory["data.records"])
    __destination_dir = path.join(ProjectDirectory["data.records_merged"])

    mergeRecords(
        source_dir = __source_dir,
        destination_filepath = path.join(__destination_dir, "" + "_mergedRecord.csv")
    )
