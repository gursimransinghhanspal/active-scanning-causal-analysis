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

from sklearn.neural_network import MLPClassifier

from globals import ProjectDirectory
from machine_learning.aux import loadNpy, selectClassifierUsingGridSearch


def trainUsingGridSearch_MLPNN(X, y, clf_savefile):
    """ """

    # parameters to tune
    param_grid = {
        'hidden_layer_sizes': [
            (16, 16, 16), (100, 100),
            (64, 128, 64)
        ],
        'activation'        : ['tanh', 'logistic', 'relu'],
        'solver'            : ['adam', 'sgd'],
        'learning_rate'     : ['constant', 'adaptive'],
        'learning_rate_init': [0.01, 0.001, 0.0001],
        'max_iter'          : [1000],
        'early_stopping'    : [True]
    }

    clf = selectClassifierUsingGridSearch(
        clf_name = 'MLP Classifier',
        clf_type = MLPClassifier,
        param_grid = param_grid,
        X = X, y = y,
        clf_savefile = clf_savefile,
        scaler_object = None
    )
    return clf


if __name__ == '__main__':
    feature_matrix = loadNpy(path.join(ProjectDirectory["data.ml"], "All_featureMatrix.npy"))
    target_vector = loadNpy(path.join(ProjectDirectory["data.ml"], "All_targetVector.npy"))
    savefile = path.join(ProjectDirectory["models"], "MLP-NN.joblib")
    #
    trainUsingGridSearch_MLPNN(feature_matrix, target_vector, savefile)
