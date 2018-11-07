import numpy as np
from sklearn.svm import SVC

from machine_learning.aux import selectClassifierUsingGridSearch


def trainUsingGridSearch_SVM(X, y, clf_savefile):
    """ """

    # testing parameters
    param_grid = {
        'kernel': ['rbf', 'linear', 'poly', 'sigmoid'],
        'C'     : np.logspace(-2, 2, 5),
        'gamma' : np.logspace(-2, 2, 5)
    }

    clf = selectClassifierUsingGridSearch(
        clf_name = 'SVM Classifier',
        clf_type = SVC,
        param_grid = param_grid,
        X = X, y = y,
        clf_savefile = clf_savefile,
        scaler_object = None
    )
    return clf


if __name__ == '__main__':
    pass
