from ReviewParser import *
from Config import get_config
config = get_config()

from PropagationRules import *

from scipy.sparse import *

def run_double_propagation(dependency_list, seed_sentiment_set, seed_feature_set, options):
    """

        Run double propagation and return a list of opinion words and a list of features
    
    :param dependency_list: List of dependencies of the sentences, obtained from the stanford parser
    :param sentiment_set: Seed opinion set dictionary to run dp
    :param feature_set: Seed opinion dictionary used to run dp (can be empty)
    :param options: dictionary of various options
    
    :return sentiment_set
    :return feature_set
    """

    # initialize the dictionaries of aspect and opinion words to be discovered
    sentiment_set = {}
    for k in seed_sentiment_set:
        sentiment_set[k] = OpinionWord(k.lower(), features_modified=set(), sentiments_modified=set(),
                                       sentences_from=set(), extracting_rules=set())

    feature_set = {}
    for k in seed_feature_set:
        feature_set[k] = FeatureWord(k.lower(), features_modified=set(), sentences_from=set(), extracting_rules=set())
   
    prev_sentiment_size = len(sentiment_set)
    prev_feature_size = len(feature_set)

    i = 1
    while True:
        # according to the paper, I run the rules in the order of 1, 4, 3, 2 
        
        # Sentiment => Attributes
        rule_one_one(dependency_list, feature_set, sentiment_set)
        
        # Sentiment => Attributes
        rule_one_two(dependency_list, feature_set, sentiment_set)

        # Sentiment => Sentiment 
        rule_four_one(dependency_list, sentiment_set)

        # Sentiment => Sentiment 
        rule_four_two(dependency_list, sentiment_set)

        # Attributes => Attributes
        rule_three_one(dependency_list, feature_set)

        # Attributes => Attributes
        rule_three_two(dependency_list, feature_set)

        # Attributes => Sentiment
        rule_two_one(dependency_list, sentiment_set, feature_set)

        # Attributes => Sentiment
        rule_two_two(dependency_list, sentiment_set, feature_set)

        # print('iteration %d finished: \#F=%d, \#O=%d' % (i, len(feature_set), len(sentiment_set)))
        
        # If this iteration of dp did not find any new elements, terminate by ranking the elements
        if (len(feature_set) - prev_feature_size) < 1 and (len(sentiment_set) - prev_sentiment_size) < 1:
            break
   
        # update the sizes
        prev_sentiment_size = len(sentiment_set)
        prev_feature_size = len(feature_set)

        i += 1
    
    return sentiment_set, feature_set


def validate_graph(opinion_set, feature_set):
    """
        Validate that each word in the feature_modified/opinion_modified is in the extracted_features/extracted_sentiments sets
    """

    for opinion_word, opinion in opinion_set.iteritems():
        for f in opinion.features_modified:
            assert f in feature_set
        for o in opinion.sentiments_modified:
            assert o in opinion_set

    for feature_word, feature in feature_set.iteritems():
        for f in feature.features_modified:
            assert f in feature_set

if __name__ == '__main__':
    """
        Testing double propagation
    """

    # load seed pickle
    with open(config.data_path + config.sentiment_seed, 'rb') as input_file:
        sentiment_dict = pickle.load(input_file)
    seed_sentiments = set(sentiment_dict.keys())

    centerfilename = [
              'Cell_Phones_and_Accessories',
              'Electronics',
              'Baby',
              'Health_and_Personal_Care',
              'Digital_Music']

    for i in xrange(0, 5):

        print(centerfilename[i])

        dependency_result = load_id_dependencies(
            config.data_path + centerfilename[i] + '/' + centerfilename[i] + '_parsed.txt')

        # the features stores with a set , initial empty
        seed_features = set()
        # the options stores with a dictionary
        options = {}
        # give a value though dp
        sentiment_set, feature_set = run_double_propagation(
            dependency_result,
            seed_sentiments,
            seed_features,
            options)

        output_filename = config.data_path + centerfilename[i] + '/' + centerfilename[i] + '_pairs.txt'
        print output_filename
        with open(output_filename, 'w') as f:
            for k in sentiment_set:
                if k.isalpha():
                    for m in sentiment_set[k].features_modified:
                        if m.isalpha():
                            if len(m) != 0:
                                n = feature_set[m].sentences_from & sentiment_set[k].sentences_from
                                if len(n) != 0:
                                    for l in n:
                                        f.write(l + ' ')
                                        f.write(k + ',')
                                        f.write(m + '\n')
            f.close()

        output_filename = config.data_path + centerfilename[i] + '/' + centerfilename[i] + '_Pairs_IDSET.txt'
        with open(output_filename, 'w') as f:
            for k in sentiment_set:
                if k.isalpha():
                    for m in sentiment_set[k].features_modified:
                        if m.isalpha():
                            if len(m) != 0:
                                n = feature_set[m].sentences_from & sentiment_set[k].sentences_from
                                if len(n) != 0:
                                    f.write(k + ' ')
                                    f.write(m + ',')
                                    f.write(' '.join(n) + '\n')
            f.close()


'''
    # combination
    with open(config.data_path + 'All electronic products_Pairs_IDSET.txt', 'w', )as file:
        for i in xrange(0, 5):
            f = config.file_names[i]
            for line in open(config.data_path + f + '_Pairs_IDSET.txt'):
                # part = line.split(' ', 1)
                file.writelines(line)
            # file.write('\n')
        file.close()

    # removal of redundancy
    pairs_set = set()
    PairsAndSet_dict = {}
    with open(config.data_path + 'All electronic products_Pairs_IDSET.txt', 'r', )as file:
        for l in file:
            tempSet = set()
            pair = l.split(',', 1)[0]
            for id in l.split(',', 1)[1].split():
                tempSet.add(id)
            if pair in pairs_set:
                PairsAndSet_dict[pair] = PairsAndSet_dict[pair] | tempSet
                print PairsAndSet_dict[pair]
                continue
            pairs_set.add(pair)
            PairsAndSet_dict[pair] = tempSet
        file.close()
    print len(pairs_set)

    # ROR write back
    with open(config.data_path + 'All electronic products_Pairs_IDSET.txt', 'w', )as f:
        for pair in pairs_set:
            f.write(pair+',')
            f.write(' '.join(PairsAndSet_dict[pair])+'\n')
        f.close()

'''







