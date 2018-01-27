"""
    This file uses the matrices produced by extraction rules and bipartite graphs
"""
import numpy as np
from scipy.sparse import *

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_curve
from sklearn.naive_bayes import MultinomialNB

from Config import get_config
config = get_config()

import pickle

def load_feature_matrices(dataset_name):
    """
        read feature matrices from various sources (ranking, rule, etc.)
        These different features are concatenated, and then the number of each group of
        features are also returned.
    """
    src_names = ['ranking', 'rule']
    src_dims = []
    data_matrics = []

    for i in xrange(len(src_names)):
        s = src_names[i]
        f = open('../results/' + dataset_name + '_' + s + '_feature_matrix.pickle', 'rb')
        X = pickle.load(f)
        if i == 0:
            src_dims.append(np.array(range(X.shape[0])))
        else:
            src_dims.append(src_dims[i-1][-1] + 1 + np.array(range(X.shape[0])))
            
        data_matrics.append(X)
        f.close()

    return np.vstack(data_matrics), src_dims

def load_label_vector(dataset_name):
    """
        read labels of words in a given domain (dataset)
    """
    f = open('../results/' + dataset_name + '_feature_label.pickle', 'rb')
    y = pickle.load(f)
    f.close()
    return y

def test_simple_fusion():
    """
        Pool all features from previous domains together, learn a model to predict words in the target domain.
        PR curves are stored to file for later plotting.
    """
    # a list containing n x d matrices of all domains, where d = d1 + d2 (pooled features)
    all_feature_matrics = []

    # a list containing n x 1 vectors of all domains
    all_label_vectors = []

    for fname in config.file_names:
        # dims are the number of features in each group, supposed to be the same across all domains.
        X, dims = load_feature_matrices(fname)
        all_feature_matrics.append(X)
        all_label_vectors.append(load_label_vector(fname))

    dataset_order = np.array(range(5))

    for i in range(5):
        # for each target domain
        fname = config.file_names[dataset_order[4]]

        training_X = []
        training_y = []
        
        # obtain data from previous 4 domains
        for j in xrange(4):
            dataset_id = dataset_order[j]
            training_X.append(all_feature_matrics[dataset_id])
            training_y.append(all_label_vectors[dataset_id])

        training_X = np.hstack(training_X)
        training_y = np.hstack(training_y)

        test_X = all_feature_matrics[dataset_order[4]]
        test_y = all_label_vectors[dataset_order[4]]

        # use ranking only, rule only or both
        feature_idx = [[0], [1], [0,1]]
        # names of feature combinations
        feature_names = ['ranking_features', 'rule_features', 'combined_features']

        # record the precision and recall arrays for each feature combinations
        pr_dict = {}
       
        # for different combinations of feature groups
        for j in xrange(len(feature_idx)):
            feature_set = feature_idx[j]

            use_dims = []
            for k in feature_set:
                use_dims.append(dims[k])
            
            use_dims = np.hstack(use_dims)

            model = MultinomialNB()
            model.fit(np.transpose(training_X)[:, use_dims], training_y.ravel())
            
            y_pred = model.predict_proba(np.transpose(test_X)[:, use_dims])[:,1]

            p, r, _ = precision_recall_curve(test_y, y_pred)
            auc = average_precision_score(test_y, y_pred)
            pr_dict[feature_names[j]] = [p, r, auc]
        
        f = open('../results/' + fname + '_snb_ff_pr_curves.pickle', 'wb')
        pickle.dump(pr_dict, f)
        f.close()
    
        dataset_order = np.roll(dataset_order, 1)

def lifelong_learning():
    """
        For each target domain, we add more and more previous domains to the training set
    """
    # a list containing n x d matrices of all domains, where d = d1 + d2 (pooled features)
    all_feature_matrics = []

    # a list containing n x 1 vectors of all domains
    all_label_vectors = []

    for fname in config.file_names:
        # dims are the number of features in each group, supposed to be the same across all domains.
        X, dims = load_feature_matrices(fname)
        all_feature_matrics.append(X)
        all_label_vectors.append(load_label_vector(fname))

    dataset_order = np.array(range(5))

    for i in range(5):
        # for each target domain
        fname = config.file_names[dataset_order[4]]
        test_X = all_feature_matrics[dataset_order[4]]
        test_y = all_label_vectors[dataset_order[4]]

        pr_dict = {}

        # obtain data from previous 4 domains
        for j in xrange(4):
            dataset_id = dataset_order[j]
            if j == 0:
                training_X = all_feature_matrics[dataset_id]
                training_y = all_label_vectors[dataset_id]
            else:
                training_X = np.hstack([training_X, all_feature_matrics[dataset_id]])
                training_y = np.hstack([training_y, all_label_vectors[dataset_id]])
            
            # test
            model = MultinomialNB()
            model.fit(np.transpose(training_X), training_y.ravel())
            
            y_pred = model.predict_proba(np.transpose(test_X))[:,1]

            p, r, _ = precision_recall_curve(test_y, y_pred)
            auc = average_precision_score(test_y, y_pred)
            pr_dict[j] = [p, r, auc]
        
        f = open('../results/' + fname + '_snb_ll_pr_curves.pickle', 'wb')
        pickle.dump(pr_dict, f)
        f.close()
    
        dataset_order = np.roll(dataset_order, 1)

def active_learning():
    """
    """
    pass

if __name__ == '__main__':
    test_simple_fusion()
    #lifelong_learning()
