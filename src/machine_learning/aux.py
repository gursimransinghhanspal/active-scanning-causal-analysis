#!python3
#
# @author: Gursimran Singh
# @rollno: 2014041
# @github: https://github.com/gursimransinghhanspal
#
# Active Scanning Causal Analysis
# Machine Learning
# |- aux.py
#       := Auxiliary Methods
#
#
from datetime import datetime
from os.path import basename

from numpy import load
from sklearn.externals import joblib
from sklearn.metrics import (accuracy_score, f1_score, make_scorer, precision_score, recall_score,
                             roc_auc_score, )
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold, train_test_split


def loadNpy(filepath):
    starttime = datetime.now()
    print("loadNpy: Loading {:s}".format(basename(filepath)), "[", starttime, "]")
    #
    npy = load(filepath)
    #
    nowtime = datetime.now()
    deltatime = nowtime - starttime
    print("loadNpy: Loaded! shape:", npy.shape, "[", nowtime, "][", deltatime.total_seconds(), "]")
    print()


def printClassifierMetrics(clf_name, y_true, y_pred, plot_cnfsn = True):
    """ """

    # Accuracy
    print("Accuracy Score:\t\t", accuracy_score(y_true, y_pred))
    # Precision
    print("Precision Score:\t\t", precision_score(y_true, y_pred, average = None))
    print("Micro Precision Score:\t\t", precision_score(y_true, y_pred, average = 'micro'))
    print("Macro Precision Score:\t\t", precision_score(y_true, y_pred, average = 'macro'))
    # Recall
    print("Recall Score:\t\t", recall_score(y_true, y_pred, average = None))
    print("Micro Recall Score:\t\t", recall_score(y_true, y_pred, average = 'micro'))
    print("Macro Recall Score:\t\t", recall_score(y_true, y_pred, average = 'macro'))
    # F1
    print("F1 Score:\t\t", f1_score(y_true, y_pred, average = None))
    print("Micro F1 Score:\t\t", f1_score(y_true, y_pred, average = 'micro'))
    print("Macro F1 Score:\t\t", f1_score(y_true, y_pred, average = 'macro'))
    #
    #
    # compute_roc_score(y_true, y_pred)
    #     # #
    #     # if plot_cnfsn:
    #     #     plot_normalized_confusion_matrix(y_true, y_pred, clf_name)


# def compute_roc_score(y_true, y_pred, n_lab):
#     y_true_binarized_labels = label_binarize(y_true, classes = range(n_lab))
#     y_pred_binarized_labels = label_binarize(y_pred, classes = range(n_lab))
#     print('AUROC Score:')
#     for i in range(n_lab):
#         try:
#             print('Class {0} v/s Rest: {1}'.format(i, roc_auc_score(
#                 y_true_binarized_labels[:, i], y_pred_binarized_labels[:, i], average = None)))
#         except Exception:
#             pass


# Plot the normalized confusion matrix.
# def plot_normalized_confusion_matrix(y_true, y_pred, plt_title):
#     class_labels = np.unique(y_true)
#     n_labels = class_labels.shape[0]
#     conf_mat = confusion_matrix(y_true, y_pred).astype(float)
#     print(conf_mat)
#     # Normalize the confusion matrix.
#     for idx in range(conf_mat.shape[0]):
#         conf_mat[idx] /= np.sum(conf_mat[idx])
#     plt.imshow(conf_mat, interpolation = 'nearest', cmap = plt.cm.Blues)
#     plt.title(plt_title)
#     plt.colorbar()
#     tick_marks = np.arange(n_labels)
#     plt.xticks(tick_marks, class_labels.astype(int))
#     plt.yticks(tick_marks, class_labels.astype(int))
#     plt.xlabel('Predicted Label')
#     plt.ylabel('Actual Label')
#     for x, y in itertools.product(range(conf_mat.shape[0]), range(conf_mat.shape[1])):
#         plt.text(y, x, format(conf_mat[x, y], '0.2f'), horizontalalignment = 'center', color = 'k')
#     plt.show()


def selectClassifierUsingGridSearch(
        clf_name,
        clf_type,
        param_grid,
        X, y,
        clf_savefile,
        scaler_object = None,
):
    """  """

    #
    starttime = datetime.now()
    print('-' * 25)
    print("Starting learning for `", clf_name, "`", "[", starttime, "]")
    print("X.shape:", X.shape, "y.shape:", y.shape)
    print('Output Filename:', basename(clf_savefile))
    print()

    # Normalize the data if required
    if scaler_object is not None:
        X = scaler_object.fit_transform(X)

    # Keep a held out set (20%, Never to be used for training)
    # NOTE: Use stratified split to get all the classes in testing set
    X_learn, y_learn, X_held, y_held = train_test_split(X, y, train_size = 0.20, stratify = y, shuffle = True)

    # Use Repeated Stratified-KFold Cross-Validation for minimal training bias
    rskf = RepeatedStratifiedKFold(5, 2)
    #
    # ***** GridSearchCrossValidation *****
    nowtime = datetime.now()
    deltatime = nowtime - starttime
    print("Starting GridSearchCV", "[", nowtime, "][", deltatime.total_seconds(), "]")
    gscv = GridSearchCV(
        estimator = clf_type(),
        param_grid = param_grid,
        cv = rskf,
        scoring = {
            'f1': make_scorer(f1_score),
            'accuracy': make_scorer(accuracy_score),
            'precision': make_scorer(precision_score),
            'recall': make_scorer(recall_score),
            'roc_auc': make_scorer(roc_auc_score),
        },
        refit = 'f1',
        verbose = 5,
        n_jobs = -1
    )
    gscv.fit(X_learn, y_learn)
    nowtime = datetime.now()
    deltatime = nowtime - starttime
    print("Completed GridSearchCV", "[", nowtime, "][", deltatime.total_seconds(), "]")
    print("Best parameters:")
    print(gscv.best_params_)
    print("Best index:")
    print(gscv.best_index_)
    print("Best score:")
    print(gscv.best_score_)
    print()
    #
    # ***** Test the classifier on held out set *****
    y_pred = gscv.predict(X_held)
    #
    print("Testing", clf_name, "on the held out data-set...")
    printClassifierMetrics(clf_name, y_held, y_pred)
    print()
    #
    # ***** Save model to file *****
    nowtime = datetime.now()
    deltatime = nowtime - starttime
    print("Training the classifier on complete data-set", "[", nowtime, "][", deltatime.total_seconds(), "]")
    the_clf = clf_type(**gscv.best_params_)
    the_clf.fit(X, y)
    #
    nowtime = datetime.now()
    deltatime = nowtime - starttime
    print("Saving to file", "[", nowtime, "][", deltatime.total_seconds(), "]")
    joblib.dump(the_clf, clf_savefile, compress = True)
    #
    nowtime = datetime.now()
    deltatime = nowtime - starttime
    print("Done", "[", nowtime, "][", deltatime.total_seconds(), "]")
    print()
    return the_clf
