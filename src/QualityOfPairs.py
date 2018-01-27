from Config import get_config
import numpy as np
from ReviewParser import load_id_dependencies
import pickle
import operator
from nltk.corpus import words
from nltk.corpus import wordnet as wn

en_words = set(words.words())

def extract_pairs(all_deps):
    """ extract amod dependency"""
    result = {}
    for dep in all_deps:
        for i in dep:
            review_deps = dep[i]
            for d in review_deps:
                if d[1] == 'amod' or d[1] == 'nsubj':
                    if d[2][1].startswith('JJ') and d[0][1].startswith('NN'):
                        if (d[2][0].lower(), d[0][0].lower()) in result:
                            result[(d[2][0].lower(), d[0][0].lower())] += 1
                        else:
                            result[(d[2][0].lower(), d[0][0].lower())] = 1
    return result

def norm_freq(pairs_frequency):
    """ normalize frequency"""
    # total_occur = 0
    # for it in pairs_frequency.items():
    #     total_occur += it[1]
    max_count = max(pairs_frequency.values())
    for key in pairs_frequency:
        # pairs_frequency[key] /= float(total_occur)
        pairs_frequency[key] /= float(max_count)
    return pairs_frequency


def load_feature_reverse_dict(fname):
    with open('../results/' + fname + '_ranking_feature_reverse_idx.pickle', 'rb') as f:
        reversed_dict = pickle.load(f)
    return reversed_dict


def load_opinion_reverse_dict(fname):
    with open('../results/' + fname + '_ranking_opinion_reverse_idx.pickle', 'rb') as f:
        reversed_dict = pickle.load(f)
    return reversed_dict


def load_feature_score(fname):
    with open('../results/' + fname + '_feature_pred_score.pickle', 'rb') as f:
        feature_pred_score = pickle.load(f)
    return feature_pred_score


def load_opinion_score(fname):
    with open('../results/' + fname + '_opinion_pred_score.pickle', 'rb') as f:
        opinion_pred_score = pickle.load(f)
    return opinion_pred_score


def get_word_idx(word, all_dict):
    """ """
    for i in range(len(all_dict)):
        if word in all_dict[i]:
            return all_dict[i][word], i
    return -1, -1


def quality_of_pairs(fname):
    """"""
    config = get_config()
    all_deps = []
    id_deps = load_id_dependencies(config.data_path + fname + '_parsed.txt')
    all_deps.append(id_deps)
    pairs_frequency = extract_pairs(all_deps)

    # with open('../results/' + 'pairs_frequency.pickle', 'wb') as f:
    #     pickle.dump(pairs_frequency, f)
    # pair: (adj, noun)
    pairs_frequency = norm_freq(pairs_frequency)

    all_feature_reverse_dict = []
    all_opinion_reverse_dict = []
    all_feature_dict = []
    all_opinion_dict = []
    all_feature_pred = []
    all_opinion_pred = []

    # load reverse dictionary
    feature_reverse_dict = load_feature_reverse_dict(fname)
    opinion_reverse_dict = load_opinion_reverse_dict(fname)
    feature_dict = dict(zip(feature_reverse_dict.values(),
                            feature_reverse_dict.keys()))
    opinion_dict = dict(zip(opinion_reverse_dict.values(),
                            opinion_reverse_dict.keys()))
    feature_pred_score = load_feature_score(fname)
    opinion_pred_score = load_opinion_score(fname)

    all_feature_reverse_dict.append(feature_reverse_dict)
    all_opinion_reverse_dict.append(opinion_reverse_dict)
    all_feature_dict.append(feature_dict)
    all_opinion_dict.append(opinion_dict)
    all_feature_pred.append(feature_pred_score)
    all_opinion_pred.append(opinion_pred_score)

    pairs_score = {}
    for pair in pairs_frequency:
        # pair[0] is Adjective
        # pair[1] is Noun
        freq = pairs_frequency[pair]
        o_word_idx, o_corp_idx = get_word_idx(pair[0], all_opinion_dict)
        a_word_idx, a_corp_idx = get_word_idx(pair[1], all_feature_dict)
        if o_word_idx > -1 and a_word_idx > -1:
            score = freq * all_feature_pred[a_corp_idx][a_word_idx] * \
                    all_opinion_pred[o_corp_idx][o_word_idx]
            pairs_score[pair] = score
    return pairs_score


def is_word(word):
    """ """
    if len(word) < 2 :
        return False
    if wn.synsets(word.lower()):
        return True
    else:
        return False


def filter_out_pairs(pairs):
    """ save pairs only if two words are appearing in English dictionary"""
    saved = []
    for p in pairs:
        if is_word(p[0][0]) and is_word(p[0][1]):
            saved.append(p)
    return saved


def top_pairs(n, pairs):
    return pairs[-n:]


def remove_scores(pairs):
    no_score_pairs = []
    for p in pairs:
        no_score_pairs.append(p[0])
    return no_score_pairs


def write_pairs_to_file(pairs, filename):
    with open(filename, 'w') as f:
        for p in pairs:
            f.write("{}, {}\n".format(p[0], p[1]))


def main():
    """"""
    # keep top n pairs
    n = 1000
    config = get_config()
    for fname in config.file_names[5:]:
        pairs_score = quality_of_pairs(fname)
        sorted_pairs = sorted(pairs_score.items(), key=operator.itemgetter(1))
        # with open('../results/amazon_reviews_sorted_pairs.pickle', 'wb') as f:
        #     pickle.dump(sorted_pairs, f)

        saved_pairs = filter_out_pairs(sorted_pairs)
        top = top_pairs(n, saved_pairs)
        no_score_pairs = remove_scores(top)
        write_pairs_to_file(no_score_pairs,
                            '../results/{0}_top{1}_pairs.txt'.format(fname, n))

if __name__ == "__main__":
    main()
