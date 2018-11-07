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
#           := Random Forest Classifier
#
#

from os import path

from sklearn.ensemble import RandomForestClassifier

from globals import ProjectDirectory
from machine_learning.aux import loadNpy, selectClassifierUsingGridSearch


def trainUsingGridSearch_RF(X, y, clf_savefile):
    """ """

    # parameters to tune
    param_grid = {
        'n_estimators': [5, 10, 20, 30, 40, 50],
        'max_depth': [None, 5, 10, 20, 30],
        'min_samples_split': [2, 5, 10]
    }

    clf = selectClassifierUsingGridSearch(
        clf_name = 'Random Forest',
        clf_type = RandomForestClassifier,
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
    savefile = path.join(ProjectDirectory["models"], "pwr_RF.joblib")
    #
    trainUsingGridSearch_RF(feature_matrix, target_vector, savefile)
