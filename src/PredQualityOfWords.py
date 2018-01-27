""" Train the MultinomialNB model from labeled datasets, first 5 set,
predict word scores on last two.
"""

import numpy as np
from Config import get_config
from sklearn.naive_bayes import MultinomialNB
from scipy.sparse import *
import pickle


def load_feature_matrices(dataset_name):
    """ """
    src_names = ['ranking', 'rule']
    src_dims = []
    data_matrics = []

    for i in range(len(src_names)):
        s = src_names[i]
        with open('../results/' + dataset_name + '_' + s + '_feature_matrix.pickle', 'rb') as f:
            feature_X = pickle.load(f)
        if i is 0:
            src_dims.append(np.array(range(feature_X.shape[0])))
        else:
            src_dims.append(src_dims[i-1][-1] + 1 + np.array(range(feature_X.shape[0])))
        data_matrics.append(feature_X)
    return np.vstack(data_matrics), src_dims


def load_opinion_matrices(dataset_name):
    """ """
    src_names = ['ranking', 'rule']
    src_dims = []
    data_matrics = []

    for i in range(len(src_names)):
        s = src_names[i]
        with open('../results/' + dataset_name + '_' + s + '_opinion_matrix.pickle', 'rb') as f:
            opinion_X = pickle.load(f)
        
        if i is 0:
            src_dims.append(np.array(range(opinion_X.shape[0])))
        else:
            src_dims.append(src_dims[i-1][-1] + 1 + np.array(range(opinion_X.shape[0])))
        data_matrics.append(opinion_X)
    return np.vstack(data_matrics), src_dims


def load_feature_labels(dataset_name):
    """"""
    with open('../results/' + dataset_name + '_feature_label.pickle', 'rb') as f:
        feature_labels = pickle.load(f)
    return feature_labels


def load_opinion_labels(dataset_name):
    """"""
    with open('../results/' + dataset_name + '_opinion_label.pickle', 'rb') as f:
        opinion_labels = pickle.load(f)
    return opinion_labels


def qualify_words():
    """ make a prediction on candidate features and opinions,
    which extracted by Double Propagation"""
    config = get_config()

    all_feature_matrices = []
    all_opinion_matrices = []

    # first 5 parts are labeled, thus are useful
    all_feature_label_vectors = []
    all_opinion_label_vectors = []

    for fname in config.file_names:
        feature_X, feature_dims = load_feature_matrices(fname)
        opinion_X, opinion_dims = load_opinion_matrices(fname)
        feature_y = load_feature_labels(fname)
        opinion_y = load_opinion_labels(fname)

        # append to all collector
        all_feature_matrices.append(feature_X)
        all_feature_label_vectors.append(feature_y)
        all_opinion_matrices.append(opinion_X)
        all_opinion_label_vectors.append(opinion_y)
    # use first 5 for training
    # stack first 5
    feature_training_X = []
    feature_training_y = []
    opinion_training_X = []
    opinion_training_y = []
    for i in range(5):
        feature_training_X.append(all_feature_matrices[i])
        feature_training_y.append(all_feature_label_vectors[i])
        opinion_training_X.append(all_opinion_matrices[i])
        opinion_training_y.append(all_opinion_label_vectors[i])

    feature_training_X = np.hstack(feature_training_X)
    feature_training_y = np.hstack(feature_training_y)
    opinion_training_X = np.hstack(opinion_training_X)
    opinion_training_y = np.hstack(opinion_training_y)

    # using combination of rule and ranking score as features
    feature_model = MultinomialNB()
    opinion_model = MultinomialNB()

    # training
    feature_model.fit(np.transpose(feature_training_X), feature_training_y.ravel())
    opinion_model.fit(np.transpose(opinion_training_X), opinion_training_y.ravel())

    # predicting on candidate aspects and opinions, extracted from amazon reviews
    for i in range(5, len(config.file_names)):
        fname = config.file_names[i]
        feature_pred = feature_model.predict_proba(
            np.transpose(all_feature_matrices[i]))[:,1]
        opinion_pred = opinion_model.predict_proba(
            np.transpose(all_opinion_matrices[i]))[:,1]
        # pickle the prediction results
        with open('../results/' + fname + '_feature_pred_score.pickle', 'wb') as f:
            pickle.dump(feature_pred, f)
        with open('../results/' + fname + '_opinion_pred_score.pickle', 'wb') as f:
            pickle.dump(opinion_pred, f)


def main():
    """ main function """
    qualify_words()

if __name__ == "__main__":
    """ main function """
    main()
