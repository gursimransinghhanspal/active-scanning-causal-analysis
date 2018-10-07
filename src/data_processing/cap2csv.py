#!python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# Preprocessor
# |- cap2csv.py
#       := Converts Wireshark/Tshark capture files (.cap/.pcap/.pcapng) to a comma separated format for easy
#          processing
#


from datetime import datetime
from os import listdir, path, waitpid
from subprocess import Popen

from src import aux
from src.globals import DefaultDirectory, FrameFields, cap_extensions


def envSetup(source_dir, destination_dir):
    aux.assertDirectoryExists(source_dir)
    aux.assertDirectoryExists(destination_dir)

    if aux.isDirectoryEmpty(source_dir):
        raise FileNotFoundError("No [cap] files to process")
    if not aux.isDirectoryEmpty(destination_dir):
        raise FileExistsError("Please clear the contents of `{:s}` to prevent any overwrites".format(
            path.basename(destination_dir)
        ))


def createShellCommandFormatString():
    """
    Use Tshark to convert capture files to csv format.
    NOTE: use tshark version 2.2.13 for consistency

    `wlan_mgt.fixed.status_code` is not required for machine learning flow, but it is required only when assigning
    rbs tags for all the causes. Including it here since storage capacity is not a big concern.
    """

    header_items = []
    for item in FrameFields:
        header_items.append(item.value)

    command = 'tshark -E separator=, -T fields '
    for item in header_items:
        command += '-e ' + item + ' '
    command += '-r \'{:s}\' >> \'{:s}\''
    return command


def createCsvHeader(ant_count = 2):
    """
    Create a csv header string for the csv files
    """

    header_items = []
    for item in FrameFields:
        header_items.append(item.value)

    # for MIMO devices, radiotap.dbm_antsignal is itself a comma separated field
    # since handling this elegantly requires much more processing, we handle this by appending extra columns to
    # the csv file which would not be used.
    # assuming MIMO 4x4 is the max (appending 4 extra headers [one for assurance])
    for i in range(ant_count - 1):
        header_items.append(FrameFields.radiotap_dbmAntsignal.value + '_' + str(i + 2))

    # join the list to form a comma separated string. also add `newline` char
    csv_header_string = str.join(',', header_items)
    csv_header_string += '\n'
    return csv_header_string


def selectCapFiles(source_dir):
    """
    Read all the cap file names present in the `source_dir`
    """

    capture_file_names = list()
    for file in listdir(source_dir):
        if path.splitext(file)[1] in cap_extensions:
            capture_file_names.append(file)

    # sort so that we always read in a predefined order
    # key: smallest file first
    capture_file_names.sort(key = lambda f: path.getsize(path.join(source_dir, f)))
    return capture_file_names


def cap2csv(
        source_dir, destination_dir,
        capture_file_names: list, command_format_string: str, csv_file_header: str,
        use_subprocesses: bool = False
):
    """
    Run the command for each file name present in `capture_file_names` list
    """

    subprocesses = list()
    for idx, capture_name in enumerate(capture_file_names):
        # base_name = capture_name without extension
        base_name = path.splitext(capture_name)[0]
        # csv_name = base_name + '.csv'
        csv_name = base_name + '.csv'

        # capture file
        capture_file = path.join(source_dir, capture_name)
        # csv file
        csv_file = path.join(destination_dir, csv_name)

        # print progress
        print('cap2csv: Starting process for file: {:s}'.format(capture_name), end = '\t\t')
        print('[', datetime.now(), ']')

        # create csv file and add header as the first line
        with open(csv_file, 'w') as file:
            file.write(csv_file_header)
            file.close()

        # run command to append data to the csv file
        #   - this can be run in parallel
        command = command_format_string.format(str(capture_file), str(csv_file))
        p = Popen(command, shell = True)

        if use_subprocesses:
            subprocesses.append(p)
        else:
            pid, exit_code = waitpid(p.pid, 0)
            print('cap2csv: Process pid {:d}, exit-code: {:d}:'.format(pid, exit_code), end = '\t\t')
            print('[', datetime.now(), ']')

    if use_subprocesses:
        exit_codes = [q.wait() for q in subprocesses]
        print('cap2csv: Exit codes for sub-processes: ', exit_codes)


if __name__ == '__main__':
    __source_dir = DefaultDirectory["data_cap"]
    __destination_dir = DefaultDirectory["data_csv"]

    envSetup(__source_dir, __destination_dir)
    cap2csv(
        __source_dir, __destination_dir,
        selectCapFiles(__source_dir), createShellCommandFormatString(), createCsvHeader(),
        False
    )
