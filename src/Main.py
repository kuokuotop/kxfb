from ReviewParser import *
from DoublePropagation import *
from Config import get_config
config = get_config()
from GraphFeatures import *
from RuleFeatures import *
#from Ranker import *
from Evaluator import *
#from Plotter import *
#from lda_gibbs import *

from scipy.sparse import *
import numpy as np

def test_dp_lda(dataset_name, seed_sentiments, dependency_result, labeled_corpus):
    """
        use lda to cluster words into two topics (0 and 1)
    """
    seed_features = set()

    options = {}

    opinion_set, feature_set = run_double_propagation(
        dependency_result,
        seed_sentiments,
        seed_features,
        options)
    
    validate_graph(opinion_set, feature_set)

    reviews = get_sentences_from_reviews( labeled_corpus)
    
    true_features = get_features_from_reviews(labeled_corpus)
    true_opinions = get_sentences_from_reviews(labeled_corpus)
    all_features = set(feature_set.keys()) | set(true_features)
    all_opinions = set(opinion_set.keys()) | set(true_opinions)

    feature_idx = dict(zip(all_features , range(len(all_features))))
    opinion_idx = dict(zip(all_opinions, range(len(all_opinions))))

    rule_feature, rule_opinion = construct_rule_word_matrices(opinion_set, feature_set, opinion_idx, feature_idx)
    
    N_TOPICS = 2
    sampler = LdaSampler(N_TOPICS)
    # doc-word matrix

    #word_rule_matrix = hstack((rule_feature, rule_opinion)).transpose()
    #word_rule_matrix = rule_feature.transpose()
    word_rule_matrix = rule_feature.transpose()
    #print np.sum(word_rule_matrix.toarray(), axis=1)

    for it, phi in enumerate(sampler.run(word_rule_matrix.toarray(), maxiter=20)):
        if it % 100 == 0:
            print( "Iteration", it )
            print( "Likelihood", sampler.loglikelihood() )
    #print sampler.p_z_d().shape
    #print word_rule_matrix.shape
    #
    #print type(sampler.p_z_d())
    #print type(word_rule_matrix.toarray())
    
    #print np.hstack((sampler.p_z_d(), word_rule_matrix.toarray()))
    #print word_rule_matrix.toarray()

def test_mixed_rule_ranking(dataset_name):
    """
        Use both detecting rules and 3 ranking scores of the feature words to predict whether a word is a valid feature or not.
    """
    # load rule-feature matrix
    f = open('../results/' + dataset_name + '_rule_feature_matrix.pickle', 'rb')
    rule_word_matrix = pickle.load(f)
    f.close()

    # load ranking-feature matrix
    f = open('../results/' + dataset_name + '_ranking_feature_matrix.pickle', 'rb')
    ranking_word_matrix = pickle.load(f)
    f.close()

    # load ground truth vector
    f = open('../results/' + dataset_name + '_feature_label.pickle', 'rb')
    y = pickle.load(f)
    f.close()
    
    dataset_order = np.array(range(5))
    for i in range(5):

        target

global_opinion_set = []
global_feature_set = []
def test_rules(seed_sentiments, dependency_result, labeled_corpus):
    """
        find out the accuracy of each rule
    """
    seed_features = set()

    options = {}

    opinion_set, feature_set = run_double_propagation(
        dependency_result,
        seed_sentiments,
        seed_features,
        options)
    global global_opinion_set
    global global_feature_set
    global_opinion_set.append(opinion_set)
    global_feature_set.append(feature_set)

    validate_graph(opinion_set, feature_set)

    reviews = get_sentences_from_reviews(labeled_corpus)
   
    # return set of true feature words
    true_features = get_features_from_reviews(labeled_corpus)
    
    # return set of true opinion words
    true_opinions = get_opinions_from_reviews(labeled_corpus)
    
    all_features = set(feature_set.keys()) | set(true_features)
    all_opinions = set(opinion_set.keys()) | set(true_opinions)

    feature_idx = dict(zip(all_features , range(len(all_features))))
    opinion_idx = dict(zip(all_opinions, range(len(all_opinions))))
    
    rule_feature, rule_opinion = construct_rule_word_matrices(opinion_set, feature_set, opinion_idx, feature_idx)
    
    #word_freq = rank_by_tf(feature_set.keys(), reviews)
    # evaluate_by_quantile(word_freq, true_features)
    
    precision, recall, rule_number = evaluate_by_rule(rule_feature.todense(), feature_idx, true_features)

    return precision, recall, rule_number

if __name__ == '__main__':
    """
        Testing double propagation
    """
    
    # with open(config.data_path + config.sentiment_seed, 'rb') as input_file:
    #    sentiment_dict = pickle.load(input_file)
   
    # seed_sentiments = set(sentiment_dict.keys())
    
    # for i in xrange(7):
    #    fname = config.file_names[i]

    #    dependency_result = load_id_dependencies(config.data_path + fname + '_parsed.txt')
       
    #    labeled_corpus = load_manual_reviews(config.data_path + fname + '_id.txt')
    
    #    precisions, recalls, rule_number = test_rules(seed_sentiments, dependency_result, labeled_corpus)

    #    f = open('../results/' + fname + '_rule_pr_points.pickle', 'wb')
    #    pickle.dump([precisions, recalls, rule_number], f)
    #    f.close()

    # import pickle
    # pickle.dump((global_opinion_set, global_feature_set), open('../opinion_and_feature.p', 'wb'))
    
    #test_dp_lda(fname, seed_sentiments, dependency_result, labeled_corpus)
    
    # bipartite graph-based ranking
    # test_Ranking()
    output_ranking_feature_matrices()
    print("write out ranking feature matrices")

    # naive bayes classifiers using word-rule matrices
    #test_single_nb()
    # test_multiple_nb()
    output_rule_feature_matrices()
    print("write out rule feature matrices")

    # for fname in config.file_names:
    #     plot_pr_performance(fname)
        # plot_lifelong_pr_performance(fname)
