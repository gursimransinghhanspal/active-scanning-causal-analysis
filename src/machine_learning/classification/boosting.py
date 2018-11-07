# !python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# Machine Learning
# |- Classification
#   |- bagging.py
#
#
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier

from machine_learning.aux import selectClassifierUsingGridSearch


def trainUsingGridSearch_Boosting(X, y, clf_savefile):
    """ """

    # testing parameters
    param_grid = {
        'loss'             : ['deviance', 'exponential'],
        'learning_rate'    : [1, 0.1, 0.01, 0.001, 0.0001],
        'n_estimators'     : [50, 100, 200, 300],
        'max_depth'        : [3, 5, 10],
        'min_samples_split': [2, 5, 10],
    }

    clf = selectClassifierUsingGridSearch(
        clf_name = 'Gradient Boosting Classifier',
        clf_type = GradientBoostingClassifier,
        param_grid = param_grid,
        X = X, y = y,
        clf_savefile = clf_savefile,
        scaler_object = None
    )
    return clf


if __name__ == '__main__':
    pass

if __name__ == '__main__':
    pass
