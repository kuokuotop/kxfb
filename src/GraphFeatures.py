"""
    Implement various ways to rank words
"""
from math import *
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import scipy

from HitsHelper import *
from ReviewParser import *
from DoublePropagation import *
from Config import get_config
config = get_config()
from Evaluator import *

def rank_by_tf(word_list, corpus, use_tfidf=False):
    """
        rank words in the descending order of term frequencies
        return: dictionary of (word:word_frequency)
    """
    vocab = dict([(word_list[i], i) for i in range(len(word_list))])

    # build a doc-term matrix out of the given corpus: keep all words
    # by default, all words are lower-cased
    v = TfidfVectorizer(vocabulary = vocab, use_idf=use_tfidf, norm=None, token_pattern=r'(?u)\b\w+[\-]*\w+\b')

    mat = v.fit_transform(corpus)
   
    tf = np.squeeze(mat.sum(axis=0))

    return dict([(word_list[i], tf[0,i]) for i in xrange(tf.shape[1])])

def rank_by_degree(word_list, feature_set, opinion_set, word_type = 'feature', ignore_same_type = True):
    """
        rank the words in the word_list, using the connection information between words
        return: dictionary of (word:word_frequency)
    """
    word_list = set(word_list)

    word_scores = {}

    if word_type == 'feature':
        # iterate the dict of opinion:OpinionWord
        for k,v in opinion_set.iteritems():
            for feature_word in v.features_modified:
                if feature_word not in word_list:
                    continue
                if feature_word in word_scores:
                    word_scores[feature_word] += 1
                else:
                    word_scores[feature_word] = 1
        if ignore_same_type == False:
            # iterate the dict of feature:FeatureWord
            for k,v in feature_set.iteritems():
                if k not in word_list:
                    continue
                # add the number of dangling words 
                if k not in word_scores:
                    word_scores[k] = len(v.features_modified)
                else:
                    word_scores[k] += len(v.features_modified)
    else:
        for k,v in opinion_set.iteritems():
            if k not in word_list:
                continue
            word_scores[k] = len(v.features_modified)
            if ignore_same_type == False:
                word_scores[k] += len(v.sentiments_modified)
    
    return [(k,v) for k, v in word_scores.iteritems()]

def rank_by_hits(feature_set, opinion_set, same_type_link=False, max_iter=30):
    """
        Use HITS on the bipartite graph of feature-opinion words
        :return dictionary of feature:hits_score and dictionary of opinion:hits_score
    """
    # rows are features, and columns are opinions
    L, feature_idx, opinion_idx = compute_matrix_feature_opinion(feature_set, opinion_set)
    
    if same_type_link:
        L_a = compute_matrix_feature(feature_set, feature_idx)
        L_o = compute_matrix_opinion(opinion_set, opinion_idx)
        L_top = scipy.sparse.hstack((L_a, L))
        L_bottom = scipy.sparse.hstack((L.transpose(), L_o))

        # this is a (feature + opinion) X (feature + opinion) matrix
        L = scipy.sparse.vstack((L_top, L_bottom))
   
    # A are the scores of rows, and H are the scores of columns
    A, H = hits(L, max_iter = max_iter)
   
    num_features = 0
    if same_type_link:
        # indices of opinions should start at num_features
        num_features = len(feature_set)
    
    return dict([(w, H[idx + num_features, 0]) for w,idx in opinion_idx.iteritems()]),\
            dict([(w, A[idx, 0]) for w,idx in feature_idx.iteritems()])

def rank_by_hits_log_frequency(hits, word_freq_dict):
    """
        fuse multiple ranking by multiplying their scores
        :param: hits is a list of pairs (word, hits_score)
        :param: word_freq_dict is a dictionary with words as keys and frequencies as values
    """
    #assert len(hits) == len(freq)
    res = []
    for cur_word, hits_score in hits.iteritems():
        if cur_word in word_freq_dict:
            freq = word_freq_dict[cur_word]
        else:
            print( cur_word + ' not found.' )
            freq = 0
        res.append((cur_word, log(1.0 + freq) * hits_score))
    return dict(res)

def output_ranking_feature_matrices():
    """
        output a 3 x # features matrix for each dataset. Each row of the matrix is the scores of the feature words according to one of the 3 ranking algorithms.
    """
    with open(config.data_path + config.sentiment_seed, 'rb') as input_file:
        sentiment_dict = pickle.load(input_file)
   
    seed_sentiments = set(sentiment_dict.keys())
    
    for i in xrange(len(config.file_names)):
        fname = config.file_names[i]

        dependency_result = load_id_dependencies(config.data_path + fname + '_parsed.txt')
        seed_features = set()
        options = {}

        opinion_set, feature_set = run_double_propagation(
            dependency_result,
            seed_sentiments,
            seed_features,
            options)
        
        validate_graph(opinion_set, feature_set)

        labeled_corpus = load_manual_reviews(config.data_path + fname + '_id.txt')
        reviews = get_sentences_from_reviews( labeled_corpus)
        
        true_features = get_features_from_reviews(labeled_corpus)
        true_opinions = get_opinions_from_reviews(labeled_corpus)
        
        all_features = set(feature_set.keys()) | set(true_features)
        all_opinions = set(opinion_set.keys()) | set(true_opinions)
        feature_idx = dict(zip(all_features, range(len(all_features))))
        opinion_idx = dict(zip(all_opinions, range(len(all_opinions))))
        
        # evaluate different ranking algorithms
        o_scores, a_scores = rank_by_hits(feature_set, opinion_set, same_type_link=False, max_iter=400)
        n_opinions = len(all_opinions)
        n_features = len(all_features)
        a_v1 = np.array([0] * n_features)
        o_v1 = np.array([0] * n_opinions)
        for k,v in a_scores.iteritems():
            a_v1[feature_idx[k]] = v
        for k, v in o_scores.iteritems():
            o_v1[opinion_idx[k]] = v

        a_word_freq = rank_by_tf(feature_set.keys(), reviews, use_tfidf=True)
        o_word_freq = rank_by_tf(opinion_set.keys(), reviews, use_tfidf=True)
        a_v2 = np.array([0] * n_features)
        o_v2 = np.array([0] * n_opinions)
        for k,v in a_word_freq.iteritems():
            a_v2[feature_idx[k]] = v
        for k, v in o_word_freq.iteritems():
            o_v2[opinion_idx[k]] = v

        a_scores = rank_by_hits_log_frequency(a_scores, a_word_freq)
        o_scores = rank_by_hits_log_frequency(o_scores, o_word_freq)
        a_v3 = np.array([0] * n_features)
        o_v3 = np.array([0] * n_opinions)
        for k,v in a_scores.iteritems():
            a_v3[feature_idx[k]] = v
        for k, v in o_scores.iteritems():
            o_v3[opinion_idx[k]] = v

        # pack these scores into a matrix
        ranking_feature_matrix = np.vstack([a_v1, a_v2, a_v3])
        ranking_opinion_matrix = np.vstack([o_v1, o_v2, o_v3])

        # dump ranking matrix
        with open('../results/' + fname + '_ranking_feature_matrix.pickle', 'wb') as f:
            pickle.dump(ranking_feature_matrix, f)
        with open('../results/' + fname + '_ranking_opinion_matrix.pickle', 'wb') as f:
            pickle.dump(ranking_opinion_matrix, f)

        # dump reverse index dictionary for features and opinions
        with open('../results/' + fname + '_ranking_feature_reverse_idx.pickle', 'wb') as f:
            feature_reverse_idx = dict(zip(feature_idx.values(),
                                           feature_idx.keys()))
            pickle.dump(feature_reverse_idx, f)
        with open('../results/' + fname + '_ranking_opinion_reverse_idx.pickle', 'wb') as f:
            opinion_reverse_idx = dict(zip(opinion_idx.values(),
                                           opinion_idx.keys()))
            pickle.dump(opinion_reverse_idx, f)
