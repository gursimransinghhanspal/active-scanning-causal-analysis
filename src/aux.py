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


def createDirectoryIfRequired(dirpath):
    if not path.exists(dirpath) or not path.isdir(dirpath):
        mkdir(dirpath)


def isDirectoryEmpty(dirpath):
    if len(listdir(dirpath)) == 0:
        return True
    return False


def selectFiles(source_dir, accepted_extensions):
    """ Read all the file names present in the `source_dir` with extension in `accepted_extensions` """

    filenames = list()
    for file in listdir(source_dir):
        if path.splitext(file)[1] in accepted_extensions:
            filenames.append(file)

    # sort so that we always read in a predefined order
    # key: smallest file first
    filenames.sort(key = lambda f: path.getsize(path.join(source_dir, f)))
    return filenames
