#!python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# |- aux.py
#       := Auxiliary Methods


from os import path, mkdir, listdir


def assertDirectoryExists(dirpath):
    if not path.exists(dirpath) or not path.isdir(dirpath):
        mkdir(dirpath)


def isDirectoryEmpty(dirpath):
    if len(listdir(dirpath)) == 0:
        return True
    return False
