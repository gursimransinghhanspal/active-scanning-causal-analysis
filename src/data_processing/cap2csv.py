#!python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# Preprocessor
# |- cap2csv.py
#       := Converts Wireshark/Tshark capture files (.cap/.pcap/.pcapng) to a pipe separated format for easy
#          processing
#

# NOTE:
# To check for radiotap protocol vs prism protocol use:
# tshark -c 1 -r $file -T fields -e frame.protocols|grep "radiotap"|wc -l
# tshark -c 1 -r $file -T fields -e frame.protocols|grep "prism"|wc -l


from datetime import datetime
from os import path, waitpid, walk
from subprocess import Popen

from src.aux import createDirectoryIfRequired, envSetup, selectFilesByExtension
from src.globals import FrameFields, ProjectDirectory, cap_extensions


def createShellCommandFormatString():
    """
    Use Tshark to convert capture files to csv format with '|' (pipe) as delimiter.

    `wlan_mgt.fixed.status_code` is not required for machine learning flow, but it is required only when assigning
    rbs tags for all the causes. Including it here since storage capacity is not a big concern.
    """

    header_items = []
    for item in FrameFields:
        header_items.append(item.value)

    command = "tshark -E separator='|' -T fields "
    for item in header_items:
        command += '-e ' + item + ' '
    command += '-r \'{:s}\' >> \'{:s}\''
    return command


def createCsvHeader():
    """ Create a csv header string for the csv files """

    header_items = []
    for item in FrameFields:
        header_items.append(item.value)

    # join the list to form a pipe separated string. also add `newline` char
    csv_header_string = str.join('|', header_items)
    csv_header_string += '\n'
    return csv_header_string


def cap2csv(
    source_dir, destination_dir, command_format_string: str, csv_header: str,
    multiprocessing: bool = False
):
    """
    Run the command for each file name present in `capture_file_names` list
    """

    subprocesses = list()
    for src_dir, _, all_files in walk(source_dir):
        print("Processing directory", path.basename(src_dir))

        # destination directory
        dst_dir = src_dir.replace(source_dir, destination_dir)
        createDirectoryIfRequired(dst_dir)

        for cap_filename in selectFilesByExtension(src_dir, all_files, cap_extensions):
            # base_name = capture filename without extension
            base_name = path.splitext(cap_filename)[0]
            csv_filename = base_name + '.csv'

            # path to files
            cap_filepath = path.join(src_dir, cap_filename)
            csv_filepath = path.join(dst_dir, csv_filename)

            # print progress
            print('cap2csv: Starting process for file: {:s}'.format(cap_filename), end = '\t\t')
            print('[', datetime.now(), ']')

            # create csv file and add header as the first line
            with open(csv_filepath, 'w') as file:
                file.write(csv_header)
                file.close()

            # run command to append data to the csv file
            # NOTE: this can be run in parallel
            command = command_format_string.format(str(cap_filepath), str(csv_filepath))
            p = Popen(command, shell = True)

            if multiprocessing:
                subprocesses.append(p)
            else:
                pid, exit_code = waitpid(p.pid, 0)
                print('cap2csv: Process pid {:d}, exit-code: {:d}:'.format(pid, exit_code), end = '\t\t')
                print('[', datetime.now(), ']')
        print()

    if multiprocessing:
        exit_codes = [q.wait() for q in subprocesses]
        print('cap2csv: Exit codes for sub-processes:')
        print(exit_codes)


if __name__ == '__main__':
    __source_dir = ProjectDirectory["data.cap"]
    __destination_dir = ProjectDirectory["data.csv"]

    envSetup(__source_dir, __destination_dir)
    cap2csv(__source_dir, __destination_dir, createShellCommandFormatString(), createCsvHeader(), False)
