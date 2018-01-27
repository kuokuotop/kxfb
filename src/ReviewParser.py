import os
from datetime import datetime
import random
import codecs
from AnnotatedReview import AnnotatedReview

import pickle

from Config import get_config
config = get_config()

def load_reviews(file_name):
    """
        This function loads reviews from Bing Liu's datasets
    """

    review_list = []
    with open(file_name, 'r',) as input_file:
        for line in input_file:
            parts = line.split('##', 1)
            # two parts and labeled
            if len(parts) == 2 and len(parts[0]) > 0:
                feature_list = []
                features = parts[0].split(',')
                #   jpeg slideshow[+2],mpeg1[+1]##
                for feature in features:
                    # get the feature    jpeg slideshow[+2]
                    if '[' in feature and len(feature[:feature.index('[')]) > 0:
                        to_add = feature[:(feature.index('['))].strip()    # jpeg slideshow
                        # We only want one word features for now, and we want to ommit those features with [u] or [p] annotations
                        if len(to_add.split()) == 1 and feature.count('[') < 2:
                            feature_list.append(feature[:(feature.index('['))].strip())
                final_feature_list = feature_list

                if len(final_feature_list) > 0:
                    sentence = parts[1].rstrip()
                    sentence = sentence.encode("utf-8").decode('utf-8', 'ignore').encode("utf-8").decode('utf-8')
                    review_list.append(AnnotatedReview('0', sentence, final_feature_list, list()))
    return review_list


def load_manual_reviews(file_name):
    review_list = []
    with codecs.open(file_name, 'r', encoding='ISO-8859-1') as input_file:
        for line in input_file:
            parts = line.strip().split(' ', 1)
            hash_code = parts[0]

            parts = parts[1].split('],[', 1)

            features = parts[0].split('[')[1]

            parts = parts[1].split('],', 1)

            opinions = parts[0]
            sentence = parts[1].encode("utf-8").decode('utf-8', 'ignore').encode("utf-8").decode('utf-8')

            review_list.append(AnnotatedReview(hash_code, sentence, features.split(','), opinions.split(',')))

    return review_list


def get_features_from_reviews(reviews_list):
    feature_set = set()
    for review in reviews_list:
        for feature in review.feature_list:
            feature_set.add(str(feature.lower()))
    return feature_set


def get_opinions_from_reviews(reviews_list):
    opinion_set = set()
    for review in reviews_list:
        for op in review.opinion_list:
            opinion_set.add(str(op.lower()))
    return opinion_set


def get_sentences_from_reviews(reviews_list):
    sentence_list = []
    for review in reviews_list:
        sentence_list.append(review.sentence.decode('utf-8', 'ignore'))
    return sentence_list


def get_hash_from_reviews(reviews_list):
    codes = []
    for review in reviews_list:
        codes.append(review.hash_code)
    return codes


def load_id_dependencies(file_name):
    id_dependencies = {}
    with open(file_name, 'r') as f:
        for line in f.readlines():
            #print line
            i, r = line.split(' ', 1)
            id_dependencies[i] = parse_dependency_from_string(r.strip())
            #print parse_dependency_from_string(r.strip())
            #break
        f.close()
    return id_dependencies


def parse_dependency_from_string(dependency_string):
    results_list = []
    dependency_string = dependency_string[1:-1]
    dependencies = dependency_string.split("),")
    for dependency in dependencies:
        try:
            dep = dependency[:dependency.index("(")].strip()
            word_a = parse_tagged_word(dependency[dependency.index("(")+1:dependency.index(",")].strip())
            word_b = parse_tagged_word(dependency[dependency.index(",")+1:].strip())
            # If we had a problem parsing a word because it was the root of the sentence, ignore that dependency
            if word_a == -1 or word_b == -1:
                continue
            results_list.append((word_a, dep, word_b))
        except Exception as e:
            print(e)
            print('dependency:', dependency)
            print('deps:', dependencies)
        #print results_list
    return results_list


def parse_tagged_word(word):
    if '/' not in word:
        return -1
    list = word.split('/')
    return (list[0], list[1])


def find_sentence_and_product(hash_code, product_reviews_map):
    for product_key in product_reviews_map:
        if hash_code in product_reviews_map[product_key].keys():
            return product_reviews_map[product_key][hash_code], product_key
    print( "could not find product for code " + str(hash_code) )


def count_occurrences(opinion_words, feature_words, sentences):
    """
    Count occurrences of opinion words and feature words in sentences
    :param opinion_words: Opinion words to be counted
    :param feature_words: Feature words to be counted
    :param sentences: Sentences containing candidate opinions and features
    """
    # reset the counts so we don't end up double counting
    for word in feature_words:
        feature_words[word].word_count = 1
    for word in opinion_words:
        opinion_words[word].word_count = 1

    for sentence in sentences:
        for word in sentence.split():
            if word.lower() in opinion_words:
                opinion_words[word.lower()].word_count += 1
            if word.lower() in feature_words:
                feature_words[word.lower()].word_count += 1

