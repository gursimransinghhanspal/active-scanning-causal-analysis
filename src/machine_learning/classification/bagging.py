#!python3
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
from sklearn.ensemble import BaggingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

from machine_learning.aux import selectClassifierUsingGridSearch


def trainUsingGridSearch_Bagging(X, y, clf_savefile):
    """ """

    # testing parameters
    param_grid = {
        'base_estimator': [KNeighborsClassifier(), GaussianNB(), DecisionTreeClassifier()],
        'n_estimators'  : [10, 20, 40, 50, 100, 200, 500],
        'max_samples'   : [0.1, 0.2, 0.25, 0.50, 0.75, 1.0],
        'max_features'  : [0.25, 0.50, 0.75, 1.0]
    }

    clf = selectClassifierUsingGridSearch(
        clf_name = 'Bagging Classifier',
        clf_type = BaggingClassifier,
        param_grid = param_grid,
        X = X, y = y,
        clf_savefile = clf_savefile,
        scaler_object = None
    )
    return clf


if __name__ == '__main__':
    pass
