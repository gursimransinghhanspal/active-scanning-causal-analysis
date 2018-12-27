from datetime import datetime
from os import path, waitpid, walk
from subprocess import Popen

from aux import createDirectoryIfRequired, selectFilesByExtension
from globals import ProjectDirectory, csv_extensions

# The path to `csv2record.py`
__exec_path = path.abspath("csv2record.py")
#
# command format string
__base_cf = "/Users/gursimransingh/Workspace/active-scanning-causal-analysis/code.git/.env/bin/python3 " + str(__exec_path) + " --ifile {:s} --ofile {:s}"
__client_cf = " --clients {:s}"
__epoch_filter_cf = " --epoch_filters {:s}"
__ap_cf = " --access_points {:s}"


def runCsv2Record(
    source_dir,
    destination_dir,
    log_dir,
    clients,
    epoch_filters,
    access_points,
    multiprocessing = False
):
    print("runCsv2Record:")
    print("\t" "src:", path.relpath(source_dir))
    print("\t" "dst:", path.relpath(destination_dir))
    print("\t" "multiprocessing:", multiprocessing)
    print()

    subprocesses = list()
    logfiles = dict()
    for src_dir, _, all_files in walk(source_dir):
        print("Processing:", path.relpath(src_dir))
        #
        # destination directory
        dst_dir = src_dir.replace(source_dir, destination_dir)
        lg_dir = src_dir.replace(source_dir, log_dir)
        createDirectoryIfRequired(dst_dir)
        createDirectoryIfRequired(lg_dir)
        #
        for csv_filename in selectFilesByExtension(src_dir, all_files, csv_extensions):
            print("•" "\t" "File:", csv_filename, end = '\t\t')
            print('[', datetime.now(), ']')
            #
            ifile = path.join(src_dir, csv_filename)
            lfile = path.join(lg_dir, path.splitext(path.basename(csv_filename))[0] + ".log")
            ofile = path.join(dst_dir, csv_filename)
            #
            command = __base_cf.format(str(path.abspath(ifile)), str(path.abspath(ofile)))
            if clients is not None and len(clients) > 0:
                command += __client_cf.format(','.join(clients))
                if epoch_filters is not None:
                    if len(epoch_filters) != len(clients):
                        raise ValueError("Epoch Filter [len] must be equal to Clients [len]!")
                    command += __epoch_filter_cf.format(','.join(epoch_filters))
            #
            if access_points is not None and len(access_points) > 0:
                command += __ap_cf.format(','.join(access_points))
            #
            print(command)
            logfile = open(lfile, mode = 'w')
            p = Popen(command, shell = True, stdout = logfile, stderr = logfile)
            logfiles[p] = logfile
            #
            if multiprocessing:
                subprocesses.append(p)
            else:
                pid, exit_code = waitpid(p.pid, 0)
                logfile.close()

                print("\t", "PID:", pid, "Exit-Code:", exit_code, end = "\t\t")
                print('[', datetime.now(), ']')
        #
        print()

    if multiprocessing:
        exit_codes = list()
        for q in subprocesses:
            ec = q.wait()
            logfiles[q].close()
            exit_codes.append(ec)

        print("Exit codes for sub-processes:")
        print(exit_codes)
    pass


if __name__ == '__main__':
    __src = ProjectDirectory["data.csv"]
    __dst = ProjectDirectory["data.record"]
    __log = path.join(ProjectDirectory["logs"], "csv2record")
    #
    createDirectoryIfRequired(__src)
    createDirectoryIfRequired(__dst)
    createDirectoryIfRequired(__log)
    #
    # runCsv2Record(
    #     source_dir = path.join(__src),
    #     destination_dir = path.join(__dst),
    #     log_dir = path.join(__log),
    #     clients = [
    #         '5c:f8:a1:14:06:a8'.lower().strip(),
    #         '00:24:2b:97:47:b8'.lower().strip(),
    #         '64:db:43:ad:db:0a'.lower().strip(),
    #         'd4:63:c6:46:dd:71'.lower().strip(),
    #         'e8:de:27:a9:4e:bb'.lower().strip(),
    #
    #         '64:70:02:2a:59:f9'.lower().strip(),
    #         '64:a2:f9:0a:4b:40'.lower().strip(),
    #         'b8:27:eb:65:e8:94'.lower().strip(),
    #         '64:a2:f9:c9:69:f9'.lower().strip(),
    #         '20:39:56:6d:44:e2'.lower().strip(),
    #
    #         '20:a6:0c:81:c1:dd'.lower().strip(),
    #         'e8:de:27:a6:75:24'.lower().strip(),
    #         'd0:df:9a:f5:68:5b'.lower().strip(),
    #         '64:db:43:ad:d9:a0'.lower().strip(),
    #         'b8:27:eb:2d:77:b0'.lower().strip(),
    #     ],
    #     epoch_filters = None,
    #     access_points = [
    #         '28:c6:8e:db:08:a5'.lower().strip(),  # probing-ap
    #     ],
    #     multiprocessing = False
    # )
    #
    #
    runCsv2Record(
        source_dir = path.join(__src),
        destination_dir = path.join(__dst),
        log_dir = path.join(__log),
        clients = None,
        epoch_filters = None,
        access_points = None,
        multiprocessing = False
    )

    # # run for [connection-establishment]
    # runCsv2Record(
    #     source_dir = path.join(__src, "ce"),
    #     destination_dir = path.join(__dst, "ce"),
    #     log_dir = path.join(__log, "ce"),
    #     clients = [
    #         '54:b8:0a:5e:f1:df'.lower().strip(),
    #         'c4:12:f5:16:90:64'.lower().strip(),
    #         'c4:12:f5:16:90:52'.lower().strip(),
    #         '54:b8:0a:5e:ed:47'.lower().strip(),
    #         '54:b8:0a:75:e9:e7'.lower().strip(),
    #         'c4:12:f5:16:90:4f'.lower().strip(),
    #         '74:da:38:35:e9:df'.lower().strip(),
    #         '6c:19:8f:b4:bc:6e'.lower().strip(),
    #     ],
    #     epoch_filters = None,
    #     access_points = [
    #         '60:e3:27:49:01:95'.lower().strip(),
    #     ],
    #     multiprocessing = False
    # )
    # #
    # # run for [ap-side-procedures]
    # runCsv2Record(
    #     source_dir = path.join(__src, "apsp"),
    #     destination_dir = path.join(__dst, "apsp"),
    #     log_dir = path.join(__log, "apsp"),
    #     clients = [
    #         '54:b8:0a:5e:f1:df'.lower().strip(),
    #         'c4:12:f5:16:90:64'.lower().strip(),
    #         'c4:12:f5:16:90:52'.lower().strip(),
    #         '54:b8:0a:5e:ed:47'.lower().strip(),
    #         '54:b8:0a:75:e9:e7'.lower().strip(),
    #         'c4:12:f5:16:90:4f'.lower().strip(),
    #         '74:da:38:35:e9:df'.lower().strip(),
    #         '6c:19:8f:b4:bc:6e'.lower().strip(),  # unexpected behavior
    #     ],
    #     epoch_filters = None,
    #     access_points = [
    #         '60:e3:27:49:01:95'.lower().strip(),
    #     ],
    #     multiprocessing = False
    # )
    # #
    # # run for [beacon-loss]
    # runCsv2Record(
    #     source_dir = path.join(__src, "bl"),
    #     destination_dir = path.join(__dst, "bl"),
    #     log_dir = path.join(__log, "bl"),
    #     clients = [
    #         '54:b8:0a:5e:f1:df'.lower().strip(),
    #         'c4:12:f5:16:90:64'.lower().strip(),
    #         'c4:12:f5:16:90:52'.lower().strip(),
    #         '54:b8:0a:5e:ed:47'.lower().strip(),
    #         '54:b8:0a:75:e9:e7'.lower().strip(),
    #         'c4:12:f5:16:90:4f'.lower().strip(),
    #         '74:da:38:35:e9:df'.lower().strip(),
    #         '6c:19:8f:b4:bc:6e'.lower().strip(),
    #     ],
    #     epoch_filters = None,
    #     access_points = [
    #         'c4:6e:1f:11:94:b8'.lower().strip(),
    #     ],
    #     multiprocessing = False
    # )
    # #
    # # run for [low-rssi]
    # runCsv2Record(
    #     source_dir = path.join(__src, "lrssi"),
    #     destination_dir = path.join(__dst, "lrssi"),
    #     log_dir = path.join(__log, "lrssi"),
    #     clients = [
    #         '64:70:02:29:c9:bc'.lower().strip(),
    #         '40:49:0f:8a:ae:59'.lower().strip(),
    #         '18:4f:32:fb:3e:e7'.lower().strip(),
    #     ],
    #     epoch_filters = None,
    #     access_points = [
    #         '28:c6:8e:db:08:a5'.lower().strip(),
    #     ],
    #     multiprocessing = False
    # )
    # #
    # # run for [assoc-periodic-scan]
    # runCsv2Record(
    #     source_dir = path.join(__src, "pscan-a"),
    #     destination_dir = path.join(__dst, "pscan-a"),
    #     log_dir = path.join(__log, "pscan-a"),
    #     clients = [
    #         '10:68:3f:77:f9:b6'.lower().strip(),
    #         '30:39:26:96:ba:3e'.lower().strip(),
    #         'b4:9c:df:d1:ea:eb'.lower().strip(),
    #         '6c:19:8f:b4:bc:6e'.lower().strip(),
    #     ],
    #     epoch_filters = None,
    #     access_points = [
    #         'a0:04:60:aa:78:40'.lower().strip(),
    #     ],
    #     multiprocessing = False
    # )
    # #
    # # run for [unassoc-periodic-scan]
    # runCsv2Record(
    #     source_dir = path.join(__src, "pscan-u"),
    #     destination_dir = path.join(__dst, "pscan-u"),
    #     log_dir = path.join(__log, "pscan-u"),
    #     clients = [
    #         '5c:f7:e6:a2:5d:14'.lower().strip(),
    #         'b4:9c:df:d1:ea:eb'.lower().strip(),
    #         'c0:ee:fb:30:d7:17'.lower().strip(),
    #         '10:68:3f:77:f9:b6'.lower().strip(),
    #         '30:39:26:96:ba:3e'.lower().strip(),
    #         '6c:19:8f:b4:bc:6e'.lower().strip(),
    #     ],
    #     epoch_filters = None,
    #     access_points = None,
    #     multiprocessing = False
    # )
    # #
    # # run for [power-state]
    # runCsv2Record(
    #     source_dir = path.join(__src, "pwr"),
    #     destination_dir = path.join(__dst, "pwr"),
    #     log_dir = path.join(__log, "pwr"),
    #     clients = [
    #         'c0:ee:fb:30:d7:17'.lower().strip(),  # unexpected behavior
    #         '64:db:43:ad:db:0a'.lower().strip(),
    #         '64:db:43:ad:d9:a0'.lower().strip(),
    #         '5c:f8:a1:14:06:a8'.lower().strip(),
    #         '80:6c:1b:d0:2e:d0'.lower().strip(),
    #     ],
    #     epoch_filters = [
    #         str(path.join(ProjectDirectory["data"], "epoch_filters", "c0_ee_fb_30_d7_17.csv")),
    #         str(path.join(ProjectDirectory["data"], "epoch_filters", "64_db_43_ad_db_0a.csv")),
    #         str(path.join(ProjectDirectory["data"], "epoch_filters", "64_db_43_ad_d9_a0.csv")),
    #         str(path.join(ProjectDirectory["data"], "epoch_filters", "5c_f8_a1_14_06_a8.csv")),
    #         str(path.join(ProjectDirectory["data"], "epoch_filters", "80_6c_1b_d0_2e_d0.csv")),
    #     ],
    #     access_points = [
    #         '28:c6:8e:db:08:a5'.lower().strip(),
    #     ],
    #     multiprocessing = False
    # )
