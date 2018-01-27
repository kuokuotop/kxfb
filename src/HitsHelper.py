#from numpy import *
import numpy as np
import numpy.linalg as nla
from scipy.sparse import *


def hits(L, row_supervision=None, col_supervision=None, tolerance=1.0e-6, max_iter=30):
    """
        Simple implementation of a hits algorithm that takes an adjacency matrix representing a bipartite graph
        :param L: the adjacency matrix
        :param row_supervision: A dictionary of word_idx with 0/1 indicating whether a row's ground truth score.
        :param col_supervision: A dictionary of word_idx with 0/1 indicating whether a column's ground truth score.
        :param tolerance: the tolerance allowed for convergence
        :param max_iter: the number of max iterations the algorithm will run through before stoping if it does
        not find convergence
        :return: a tuple containing the authority values and the hub values for the given graph
        """

    n, m = L.shape

    # random initialization: uniform in [0,1)
    A = np.random.rand(n, 1)    # authority scores on the rows
    H = np.random.rand(m, 1)    # hub scores on the columns
  
    if row_supervision is not None:
        for k,v in row_supervision.iteritems():
            A[k, 0] = v
    
    if col_supervision is not None:
        for k,v in col_supervision.iteritems():
            H[k, 0] = v

    # for faster computation
    L = csr_matrix(L)
    Lt = L.transpose()

    # row-normalization L
    s = L.sum(axis=1)
    z = np.where(s==0)[0]   # worry about the zeros
    s[z] = 1.0
    L = diags(1./np.squeeze(np.asarray(s))).dot(L)

    # row-normalization Lt
    s = Lt.sum(axis=1)
    z = np.where(s==0)[0]
    s[z] = 1.0
    Lt = diags(1./np.squeeze(np.asarray(s))).dot(Lt)
    
    for j in range(max_iter):
        old_A = A
        old_H = H
        A = L.dot(H)   # (n, m) x m 
        H = Lt.dot(A)    # (m, n) x n, use the new A to get the new H

        # normalize the scores to be between 0 and 1
        A = A / np.amax(A)
        H = H / np.amax(H)
  
        # clip the scores of the words that are in the supervised sets
        if row_supervision is not None:
            for k,v in row_supervision.iteritems():
                A[k, 0] = v
        
        if col_supervision is not None:
            for k,v in col_supervision.iteritems():
                H[k, 0] = v
        
        err_a = nla.norm(old_A - A)
        err_h = nla.norm(old_H - H)

        if err_a < n*tolerance and err_h < n*tolerance:
            return A,H 
    return A, H 


def compute_matrix_feature_opinion(feature_words, opinion_words, feature_idx = None, opinion_idx = None):
    """
    return: a len(feature_words) by len(opinion_words) sparse matrix
            a dictionary mapping feature words to their indices in the matrix
            a dictionary mapping opinion words to their indices in the matrix
    """
    data = []
    i = []
    j = []
  
    
    #for k,v in opinion_words.iteritems():
    #    print k
    #    print v.features_modified 
    # opinion_words may contain dangling words
    if opinion_idx is None:
        # construct mappings from opinion words to their indices in the L matrix
        opinions = [k for k,v in opinion_words.iteritems()]
        opinion_idx = dict(zip(opinions, range(len(opinions))))
    
    # feature_words may contain dangling words
    if feature_idx is None:
        features = [k for k,v in feature_words.iteritems()]
        feature_idx = dict(zip(features, range(len(features))))
    
    # only consider opinion-feature connections
    for opinion_word, opinion in opinion_words.iteritems():
        r = opinion_idx[opinion_word]
        for word in opinion.features_modified:
            #for feature in feature_words:
            #if feature.word in opinion.features_modified:
            c = feature_idx[word]
            data.append(1)
            i.append(r)
            j.append(c)
    return coo_matrix((data, (i,j)), shape=(len(opinions),len(features)) ).transpose(), feature_idx, opinion_idx


def compute_matrix_feature(feature_words, feature_idx):
    data = []
    i = []
    j = []
  
    for feature_word, feature in feature_words.iteritems():
        r = feature_idx[feature_word]
        for word in feature.features_modified:
            c = feature_idx[word]
            data.append(1)
            i.append(r)
            j.append(c)
            data.append(1)
            i.append(c)
            j.append(r)
    return coo_matrix((data, (i,j)), shape=(len(feature_idx),len(feature_idx)))
    
def compute_matrix_opinion(opinion_words, opinion_idx):
    data = []
    i = []
    j = []
  
    for opinion_word, opinion in opinion_words.iteritems():
        r = opinion_idx[opinion_word]
        for word in opinion.sentiments_modified:
            c = opinion_idx[word]
            data.append(1)
            i.append(r)
            j.append(c)
            data.append(1)
            i.append(c)
            j.append(r)
    return coo_matrix((data, (i,j)), shape=(len(opinion_idx),len(opinion_idx)) )
