#!python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# |- aux.py
#       := Auxiliary Methods


from os import listdir, mkdir, path
import fnmatch


def createDirectoryIfRequired(dirpath):
    if not path.exists(dirpath) or not path.isdir(dirpath):
        mkdir(dirpath)


def isDirectoryEmpty(dirpath):
    if len(listdir(dirpath)) == 0:
        return True
    return False


def selectFilesByExtension(source_dir, filenames, accepted_extensions):
    filtered_filenames = set()
    for extension in accepted_extensions:
        fn_filter = fnmatch.filter(filenames, "*" + extension)
        for item in fn_filter:
            filtered_filenames.add(item)

    filtered_filenames = list(filtered_filenames)
    # sort so that we always read in a predefined order
    # key: smallest file first
    filtered_filenames.sort(key = lambda f: path.getsize(path.join(source_dir, f)))
    return filtered_filenames


def envSetup(source_dir, destination_dir):
    createDirectoryIfRequired(source_dir)
    createDirectoryIfRequired(destination_dir)

    if isDirectoryEmpty(source_dir):
        raise FileNotFoundError("No files to process in {:s}".format(
            path.basename(source_dir)
        ))
    if not isDirectoryEmpty(destination_dir):
        raise FileExistsError("Please clear the contents of `{:s}` to prevent any overwrites".format(
            path.basename(destination_dir)
        ))
