from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
from sklearn.metrics import roc_auc_score

import numpy as np
from scipy.stats.mstats import mquantiles

import matplotlib.pyplot as plt

import pickle

def compute_pr_curve(word_with_scores, true_words):
    """
    :param: word_with_scores are the list of retrieved words with their scores
    :param: true_word are the set of true opinion/feature words
    """
    if type(word_with_scores) is dict:
        word_with_scores = [(k,v) for k,v in word_with_scores.iteritems()]
    retrieved_words, scores = zip(*word_with_scores)
    all_words = set(retrieved_words).union(true_words)
    false_neg = true_words - set(retrieved_words)
    
    # the retrieved scores come first, then the scores for the false negatives
    y_scores= list(scores) + [0] * len(false_neg)

    # every label is 1 except those not in true_words
    y_true = [1] * len(all_words)
    for i in xrange(len(retrieved_words)):
        if retrieved_words[i] not in true_words:
            y_true[i] = 0

    precision, recall, _ = precision_recall_curve(y_true, y_scores)
    pr_score = average_precision_score(y_true, y_scores)

    return (precision, recall, pr_score)

def compute_pr(retrieved_words, true_words):
    """
        retrieved_words: set of words retrieved by an algorithm
        true_words: set of all true positive words
        return: precision and recall
    """
    true_positives = retrieved_words & true_words
    precision = float(len(true_positives)) / len(retrieved_words)
    recall = float(len(true_positives)) / len(true_words)
    return precision, recall

def evaluate_by_quantile(word_freq, true_words):
    """
        evaluate the performance of a rule on different quantiles of word frequency
    """
    
    # array of word frequencies
    frequencies = [v for k,v in word_freq.iteritems()]
    
    quantiles = np.hstack((np.array([0]), mquantiles(frequencies), np.array(max(frequencies))))
    hist, bin_edges = np.histogram(frequencies, bins=quantiles)
    
    bin_of_words = {}
    for word, freq in word_freq.iteritems():
        # find a bin for this word
        for i in xrange(len(quantiles)-1):
            if freq <= bin_edges[i+1] and freq > bin_edges[i]:
                if i not in bin_of_words:
                    bin_of_words[i] = set()
                bin_of_words[i].add(word)
                break
    
    for b, retrieved_words in bin_of_words.iteritems():
        p, r = compute_pr(retrieved_words, true_words)
        print( 'quantile %d has %d words with precision=%f, recall=%f' % (b, len(retrieved_words), p, r))
def evaluate_by_rule(rule_feature_matrix, feature_idx, true_words):
    """
        Evaluate the precision and recall of each rule
        :param: rule_feature_matrix is a binary matrix, indicating which word is discovered by which rule
        :param: feature_idx is a map from feature words to their indices
        :param: true_words is a set of positive words

        :return: # of correctly retrieved words (list of 8), # of retrieved words in total (array of 8), and the number of truely positive words
    """
    num_rules, num_words = rule_feature_matrix.shape

    idx_feature = dict([(v, k) for k,v in feature_idx.iteritems()])
    
    precisions = []
    recalls = []
    rule_number = []

    for i in xrange(num_rules):
        nz = np.nonzero(rule_feature_matrix[i,:])[1].flatten().tolist()
        retrieved_words = set([idx_feature[j] for j in nz])
        if len(retrieved_words) == 0:
            continue
        p, r = compute_pr(retrieved_words, true_words)
        precisions.append(p)
        recalls.append(r)
        rule_number.append(i)

    return precisions, recalls, rule_number

def plot_pr_performance(dataset_name):
    """
        Compare the performance of multiple naive bayes transfer with single naive bayes, graph-based and single rule ranking performance

        :param dataset_name: the name of the dataset on which the performances are compared
    """
    plt.clf()

    # load and plot (precision, recall) points resulting from single rules
    # marker styles
    m = ['x', 'o', '+', '^', 's', 'h']
    f = open('../results/' + dataset_name + '_rule_pr_points.pickle', 'rb')
    precisions, recalls, rule_number = pickle.load(f)
    for i in xrange(len(precisions)):
        plt.scatter(recalls[i], precisions[i], marker=m[i], color='g')
        plt.annotate(str(rule_number[i]), xy=(recalls[i], precisions[i]))
    f.close()
    
    # load and plot precision-recall curves resulting from graph-based rankers
    # markers and line styles
    styles = ['--', '-.', ':']
    f = open('../results/' + dataset_name + '_graph_pr_curves.pickle', 'rb')
    res = pickle.load(f)
    f.close()
    i = 0
    for k,v in res.iteritems():
        precision = v[0]
        recall = v[1]
        auc = v[2]
        plt.plot(recall, precision, linestyle=styles[0], marker = m[i], color='r', label=k)
        i += 1
    
    # load precision-recall curves resulting from single naive bayes classifier using different set of features
    f = open('../results/' + dataset_name + '_snb_ff_pr_curves.pickle', 'rb')
    pr_dict = pickle.load(f)
    f.close()
    i = 0
    for k,v in pr_dict.iteritems():
        precision = v[0]
        recall = v[1]
        auc = v[2]
        plt.plot(recall, precision, linestyle=styles[0], marker = m[i], color='b', label=k)
        i += 1
    
    # post-processing of the figure
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.legend(loc='upper left',bbox_to_anchor=(1, 0.5))
    plt.title('Comparison of Precision-Recall Curves')
    plt.savefig('../results/' + dataset_name + '.png')

def plot_lifelong_pr_performance(dataset_name):
    """
        Plot how the performance evolves as more and more domains are added.
    """
    plt.clf()
    m = ['x', 'o', '+', '^', 's', 'h']
    styles = ['--', '-.', ':']
    colors = ['r', 'g', 'b', 'k']

    f = open('../results/' + dataset_name + '_snb_ll_pr_curves.pickle', 'rb')
    res = pickle.load(f)
    f.close()

    i = 0
    for k,v in res.iteritems():
        precision = v[0]
        recall = v[1]
        auc = v[2]
        plt.plot(recall, precision, linestyle=styles[0], marker = m[i], color=colors[i], label=k)
        i += 1
    
    # post-processing of the figure
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.legend(loc='upper left',bbox_to_anchor=(1, 0.5))
    plt.title('Lifelong learning comparison of Precision-Recall Curves')
    plt.savefig('../results/' + dataset_name + '_ll.png')

