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

from globals import MLFeaturesForCause, csv_extensions, ProjectDirectory, ASCause, WindowMetrics
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
    records_dataframe.dropna(inplace = True)
    return records_dataframe[fields]


def mergeRecords(source_dir, destination_filepath, fields):
    """ """

    file_df = pd.DataFrame(columns = fields)
    file_df.to_csv(destination_filepath, mode = 'w', sep = ',', index = False, header = True, columns = fields)

    for src_dir, _, all_files in walk(source_dir):
        print("Processing directory", path.basename(src_dir))
        print()

        for csv_filename in selectFilesByExtension(src_dir, all_files, csv_extensions):
            file_df = readRecordsFile(path.join(src_dir, csv_filename), fields)
            file_df.to_csv(destination_filepath, mode = 'a', sep = ',', index = False, header = False, columns = fields)


if __name__ == '__main__':
    __source_dir = path.join(ProjectDirectory["data.records"], "pscan-u")
    __destination_dir = path.join(ProjectDirectory["data.records_merged"])

    mergeRecords(
        source_dir = __source_dir,
        # destination_filepath = path.join(__destination_dir, "pwr" + "_mergedRecord.csv"),
        destination_filepath = path.join(__destination_dir, "pscan_u" + "_mergedRecord_nonnull.csv"),
        fields = WindowMetrics.valuesAsList()
    )
