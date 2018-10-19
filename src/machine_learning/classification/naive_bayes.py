#!python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# Machine Learning
# |- Classification
#   |- random_forest.py
#           := Auxiliary Methods
#
#

from os import path

from sklearn.naive_bayes import GaussianNB

from globals import ProjectDirectory
from machine_learning.aux import loadNpy, selectClassifierUsingGridSearch


def trainUsingGridSearch_RF(X, y, clf_savefile):
    """ """

    # parameters to tune
    param_grid = {

    }

    clf = selectClassifierUsingGridSearch(
        clf_name = 'Naive Bayes',
        clf_type = GaussianNB,
        param_grid = param_grid,
        X = X, y = y,
        clf_savefile = clf_savefile,
        scaler_object = None
    )
    return clf


def test(clf_savefile, X):
    pass


if __name__ == '__main__':
    feature_matrix = loadNpy(path.join(ProjectDirectory["data.ml"], "pwr_OneVsAll_featureMatrix.npy"))
    target_vector = loadNpy(path.join(ProjectDirectory["data.ml"], "pwr_OneVsAll_targetVector.npy"))
    savefile = path.join(ProjectDirectory["models"], "pwr_NB.joblib")
    #
    trainUsingGridSearch_RF(feature_matrix, target_vector, savefile)
