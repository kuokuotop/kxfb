from ReviewParser import *
from DoublePropagation import *
from Config import get_config
config = get_config()

import numpy as np
from scipy.sparse import *

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_curve
from sklearn.naive_bayes import MultinomialNB

import pickle

def construct_rule_word_matrices(feature_set, opinion_set, feature_idx, opinion_idx):
    """
        rule-word matrix
    """
    data = []
    i = []
    j = []
    for k, v in feature_set.iteritems():
        if len(v.extracting_rules) == 0:
            print( k + " has no extracting rule" )
        for rule in v.extracting_rules:
            i.append(rule - 1)
            j.append(feature_idx[k])
            data.append(1)
    rule_feature = coo_matrix((data, (i, j)), shape=(8, len(feature_idx)))

    data = []
    i = []
    j = []
    for k, v in opinion_set.iteritems():
        for rule in v.extracting_rules:
            i.append(rule - 1)
            j.append(opinion_idx[k])
            data.append(1)
    rule_opinion = coo_matrix((data, (i, j)), shape=(8, len(opinion_idx)))

    return rule_feature, rule_opinion


def construct_ground_truth_vector(true_features, true_opinions, feature_idx, opinion_idx):
    """
        feature_idx: map a feature word to its index. Feature words is the union of true feature words and retrived words
    """
    feature_labels = [0] * len(feature_idx)
    for w in true_features:
        feature_labels[feature_idx[w]] = 1

    opinion_labels = [0] * len(opinion_idx)
    for w in true_opinions:
        opinion_labels[opinion_idx[w]] = 1

    return np.array(feature_labels)[:, np.newaxis], np.array(opinion_labels)[:, np.newaxis]

def text_to_matrix(fname, seed_sentiments):
    """
        Construct word_rule matrices and label vectors
    """
    dependency_result = load_id_dependencies(config.data_path + fname + '_parsed.txt')
    seed_features = set()
    options = {}

    opinion_set, feature_set = run_double_propagation(
        dependency_result,
        seed_sentiments,
        seed_features,
        options)

    labeled_corpus = load_manual_reviews(config.data_path + fname + '_id.txt')
    
    true_features = get_features_from_reviews(labeled_corpus)
    true_opinions = get_opinions_from_reviews(labeled_corpus)

    all_features = set(feature_set.keys()) | set(true_features)
    all_opinions = set(opinion_set.keys()) | set(true_opinions)

    feature_idx = dict(zip(all_features , range(len(all_features))))
    opinion_idx = dict(zip(all_opinions, range(len(all_opinions))))
    
    rule_feature, rule_opinion = construct_rule_word_matrices(feature_set, opinion_set, feature_idx, opinion_idx)
    feature_label, opinion_label = construct_ground_truth_vector(true_features, true_opinions, feature_idx, opinion_idx)
    
    feature_x = rule_feature.transpose().todense()
    feature_y = feature_label
    opinion_x = rule_opinion.transpose().todense()
    opinion_y = opinion_label

    return feature_x, feature_y, opinion_x, opinion_y

def output_rule_feature_matrices():
    """
        write rule_feature (along with ground truth) matrices to files
    """
    with open(config.data_path + config.sentiment_seed, 'rb') as input_file:
        sentiment_dict = pickle.load(input_file)
    seed_sentiments = set(sentiment_dict.keys())
   
    for i in range(len(config.file_names)):
        if i is 5:
            print('processing ', config.file_names[i])
        fname = config.file_names[i]
        feature_x, feature_y, opinion_x, opinion_y = text_to_matrix(
            fname, seed_sentiments)
        feature_x = np.transpose(feature_x)
        opinion_x = np.transpose(opinion_x)
        with open('../results/' + fname + '_rule_feature_matrix.pickle', 'wb') as f:
            pickle.dump(feature_x, f)
        with open('../results/' + fname + '_rule_opinion_matrix.pickle', 'wb') as f:
            pickle.dump(opinion_x, f)

        with open('../results/' + fname + '_feature_label.pickle', 'wb') as f:
            pickle.dump(feature_y.ravel(), f)
        with open('../results/' + fname + '_opinion_label.pickle', 'wb') as f:
            pickle.dump(opinion_y.ravel(), f)
