#!python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# Machine Learning
# |- main.py
#
#
from os import path

from globals import ProjectDirectory, ASCause
from machine_learning.aux import loadNpy
from machine_learning.classification.mlp_nn import trainUsingGridSearch_MLPNN


def train_NN_fullFeatureSet():
    directory = path.join(ProjectDirectory["data.ml"], "fullFeatureSet", "sampled")
    #
    print("Training MLP Neural Net (full-features)")
    X = loadNpy(path.join(directory, "fullFeatureSet_equalSample_featureMatrix.npy"))
    y = loadNpy(path.join(directory, "fullFeatureSet_equalSample_targetVector.npy"))
    savefile = path.join(ProjectDirectory["models"], "fullFeatureSet_equalSample_NN.joblib")
    #
    print("*" * 80)
    trainUsingGridSearch_MLPNN(X, y, savefile)
    print("*" * 80)
    print()


def train_NN_selectedFeatureSet():
    directory = path.join(ProjectDirectory["data.ml"], "selectedFeatureSet", "sampled")
    #
    for cause in ASCause:
        print("Training MLP Neural Net (selected-features)", cause.name)
        #
        X = loadNpy(path.join(directory, "selectedFeatureSet_equalSample_" + cause.name + "_featureMatrix.npy"))
        y = loadNpy(path.join(directory, "selectedFeatureSet_equalSample_" + cause.name + "_targetVector.npy"))
        savefile = path.join(ProjectDirectory["models"], "selectedFeatureSet_equalSample_" + cause.name + "_NN.joblib")
        #
        print("*" * 80)
        trainUsingGridSearch_MLPNN(X, y, savefile)
        print("*" * 80)
        print()


if __name__ == '__main__':
    print("=" * 80)
    train_NN_fullFeatureSet()
    print("=" * 80)
    train_NN_selectedFeatureSet()
    print("=" * 80)
