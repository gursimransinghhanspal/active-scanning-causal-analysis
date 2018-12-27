from datetime import datetime
from os import path, walk

from aux import selectFilesByExtension
from globals import FrameFields, csv_extensions, ProjectDirectory
from data_processing.csv2record import readCsvFile


def findClientsAssociatedWith(source_dir, ap_bssid):
    """ """

    client_mac_addresses = set()
    #
    for src_dir, _, all_files in walk(source_dir):
        print("Processing:", path.relpath(src_dir))
        #
        for csv_filename in selectFilesByExtension(src_dir, all_files, csv_extensions):
            print("•" "\t" "File:", csv_filename, end = '\t\t')
            print('[', datetime.now(), ']')
            #
            ifile = path.join(src_dir, csv_filename)
            #
            # process csv file
            in_df = readCsvFile(ifile)
            #
            client_mac_addresses.update(
                in_df[in_df[FrameFields.wlan_bssid.v] == ap_bssid][FrameFields.wlan_sa.v].unique()
            )
        #
        print()

    print("Clients Detected:")
    for client in client_mac_addresses:
        print(client)


if __name__ == '__main__':
    findClientsAssociatedWith(ProjectDirectory["data.csv"], '60:e3:27:49:01:95')
