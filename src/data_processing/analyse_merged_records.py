from os import path

import pandas as pd

from globals import ProjectDirectory, Features


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
    return records_dataframe[fields]


def analyse_apsp(filepath):
    print("*" * 80)
    print("AP Side Procedures")
    print("*" * 80)
    print()
    ##
    withna = readRecordsFile(filepath, Features.valuesAsList())
    withna_uniq = withna.drop_duplicates(inplace = False)
    #
    print("(with-na)" "\t" "all:", withna.shape)
    print("(with-na)" "\t" "unique:", withna_uniq.shape)
    print(
        "(with-na)" "\t" "1 in ap_disconnection_frames__binary:" "\t",
        (withna_uniq[withna_uniq[Features.ap_disconnection_frames__binary.v] == 1]).shape
    )
    print()
    ##
    dropna = withna.dropna(inplace = False)
    dropna_uniq = dropna.drop_duplicates(inplace = False)
    #
    print("(drop-na)" "\t" "all:" "\t", dropna.shape)
    print("(drop-na)" "\t" "unique:" "\t", dropna_uniq.shape)
    print(
        "(drop-na)" "\t" "1 in ap_disconnection_frames__binary:" "\t",
        (dropna_uniq[dropna_uniq[Features.ap_disconnection_frames__binary.v] == 1]).shape
    )
    #
    print()
    print("*" * 80)
    print()


def analyse_bl(filepath):
    print("*" * 80)
    print("Beacon Loss")
    print("*" * 80)
    print()
    ##
    withna = readRecordsFile(filepath, Features.valuesAsList())
    withna_uniq = withna.drop_duplicates(inplace = False)
    #
    print("(with-na)" "\t" "all:", withna.shape)
    print("(with-na)" "\t" "unique:", withna_uniq.shape)
    print(
        "(with-na)" "\t" "1 in directed_probe_requests__binary:" "\t",
        (withna_uniq[withna_uniq[Features.directed_probe_requests__binary.v] == 1]).shape
    )
    print()
    ##
    dropna = withna.dropna(inplace = False)
    dropna_uniq = dropna.drop_duplicates(inplace = False)
    #
    print("(drop-na)" "\t" "all:" "\t", dropna.shape)
    print("(drop-na)" "\t" "unique:" "\t", dropna_uniq.shape)
    print(
        "(drop-na)" "\t" "1 in directed_probe_requests__binary:" "\t",
        (dropna_uniq[dropna_uniq[Features.directed_probe_requests__binary.v] == 1]).shape
    )
    #
    print()
    print("*" * 80)
    print()


def analyse_ce(filepath):
    print("*" * 80)
    print("Connection Establishment")
    print("*" * 80)
    print()
    ##
    withna = readRecordsFile(filepath, Features.valuesAsList())
    withna_uniq = withna.drop_duplicates(inplace = False)
    #
    print("(with-na)" "\t" "all:", withna.shape)
    print("(with-na)" "\t" "unique:", withna_uniq.shape)
    print(
        "(with-na)" "\t" "1 in client_connection_frame__binary:" "\t",
        (withna_uniq[withna_uniq[Features.client_connection_frame__binary.v] == 1]).shape
    )
    print()
    ##
    dropna = withna.dropna(inplace = False)
    dropna_uniq = dropna.drop_duplicates(inplace = False)
    #
    print("(drop-na)" "\t" "all:" "\t", dropna.shape)
    print("(drop-na)" "\t" "unique:" "\t", dropna_uniq.shape)
    print(
        "(drop-na)" "\t" "1 in client_connection_frame__binary:" "\t",
        (dropna_uniq[dropna_uniq[Features.client_connection_frame__binary.v] == 1]).shape
    )
    #
    print()
    print("*" * 80)
    print()


def analyse_lrssi(filepath):
    print("*" * 80)
    print("Low RSSI")
    print("*" * 80)
    print()
    ##
    withna = readRecordsFile(filepath, Features.valuesAsList())
    withna_uniq = withna.drop_duplicates(inplace = False)
    #
    print("(with-na)" "\t" "all:", withna.shape)
    print("(with-na)" "\t" "unique:", withna_uniq.shape)
    print()
    ##
    dropna = withna.dropna(inplace = False)
    dropna_uniq = dropna.drop_duplicates(inplace = False)
    #
    print("(drop-na)" "\t" "all:" "\t", dropna.shape)
    print("(drop-na)" "\t" "unique:" "\t", dropna_uniq.shape)
    #
    print()
    print("*" * 80)
    print()


def analyse_pscana(filepath):
    print("*" * 80)
    print("Associated Periodic Scan")
    print("*" * 80)
    print()
    ##
    withna = readRecordsFile(filepath, Features.valuesAsList())
    withna_uniq = withna.drop_duplicates(inplace = False)
    #
    print("(with-na)" "\t" "all:", withna.shape)
    print("(with-na)" "\t" "unique:", withna_uniq.shape)
    print(
        "(with-na)" "\t" "1 in sleep_frames__binary:" "\t",
        (withna_uniq[withna_uniq[Features.sleep_frames__binary.v] == 1]).shape
    )
    print()
    ##
    dropna = withna.dropna(inplace = False)
    dropna_uniq = dropna.drop_duplicates(inplace = False)
    #
    print("(drop-na)" "\t" "all:" "\t", dropna.shape)
    print("(drop-na)" "\t" "unique:" "\t", dropna_uniq.shape)
    print(
        "(drop-na)" "\t" "1 in sleep_frames__binary:" "\t",
        (dropna_uniq[dropna_uniq[Features.sleep_frames__binary.v] == 1]).shape
    )
    #
    print()
    print("*" * 80)
    print()


def analyse_pscanu(filepath):
    print("*" * 80)
    print("Unassociated Periodic Scan")
    print("*" * 80)
    print()
    ##
    withna = readRecordsFile(filepath, Features.valuesAsList())
    withna_uniq = withna.drop_duplicates(inplace = False)
    #
    print("(with-na)" "\t" "all:", withna.shape)
    print("(with-na)" "\t" "unique:", withna_uniq.shape)
    print(
        "(with-na)" "\t" "0 in client_associated__binary:" "\t",
        (withna_uniq[withna_uniq[Features.client_associated__binary.v] == 0]).shape
    )
    print()
    ##
    dropna = withna.dropna(inplace = False)
    dropna_uniq = dropna.drop_duplicates(inplace = False)
    #
    print("(drop-na)" "\t" "all:" "\t", dropna.shape)
    print("(drop-na)" "\t" "unique:" "\t", dropna_uniq.shape)
    print(
        "(drop-na)" "\t" "0 in client_associated__binary:" "\t",
        (dropna_uniq[dropna_uniq[Features.client_associated__binary.v] == 0]).shape
    )
    #
    print()
    print("*" * 80)
    print()


def analyse_pwr(filepath):
    print("*" * 80)
    print("Power State")
    print("*" * 80)
    print()
    ##
    withna = readRecordsFile(filepath, Features.valuesAsList())
    withna_uniq = withna.drop_duplicates(inplace = False)
    #
    print("(with-na)" "\t" "all:", withna.shape)
    print("(with-na)" "\t" "unique:", withna_uniq.shape)
    print()
    ##
    dropna = withna.dropna(inplace = False)
    dropna_uniq = dropna.drop_duplicates(inplace = False)
    #
    print("(drop-na)" "\t" "all:" "\t", dropna.shape)
    print("(drop-na)" "\t" "unique:" "\t", dropna_uniq.shape)
    #
    print()
    print("*" * 80)
    print()


if __name__ == '__main__':
    analyse_apsp(path.join(ProjectDirectory["data.records_merged"], "apsp_mergedRecord.csv"))
    analyse_bl(path.join(ProjectDirectory["data.records_merged"], "bl_mergedRecord.csv"))
    analyse_ce(path.join(ProjectDirectory["data.records_merged"], "ce_mergedRecord.csv"))
    analyse_lrssi(path.join(ProjectDirectory["data.records_merged"], "lrssi_mergedRecord.csv"))
    analyse_pscana(path.join(ProjectDirectory["data.records_merged"], "pscanA_mergedRecord.csv"))
    analyse_pscanu(path.join(ProjectDirectory["data.records_merged"], "pscanU_mergedRecord.csv"))
    analyse_pwr(path.join(ProjectDirectory["data.records_merged"], "pwr_mergedRecord.csv"))
