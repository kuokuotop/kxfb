from FeatureWord import FeatureWord
from OpinionWord import OpinionWord

mr_list = ["mod", "amod", "nmod", "nsubj", "nsubjpass", "obj", "dobj", "iobj"]
noun_list = ["NN", "NNP", "NNS", "NNPS"]
adjective_list = ["JJ", "JJR", "JJS"]
mod_list = ["mod", "amod", "nmod"]
subj_list = ["nsubj", "nsubjpass", "obj", "dobj", "iobj"]


# Note the original double propagation paper uses looser dependencies than the stanford parser, so this is a rough
# mapping
# this rule is important to find many features
def rule_one_one(sentence_dependency_dict, extracted_features, extracted_sentiments):
    
    for hash_code in sentence_dependency_dict:
        sentence = sentence_dependency_dict[hash_code]
        for dependency in sentence:
            word = dependency[2][0].lower()  # O
            dependency_type = dependency[1]  # O-Dep
            dependent = dependency[0][0].lower()  # T
            
            # if word is already in the fetched opinion words, and dep type is in mr_list and the POS tag of the dependent is in nout_list
            if word in extracted_sentiments and check_dependency(dependency_type, mr_list) and check_pos(
                    dependency[0][1], noun_list):
                # print word + ' ' + dependency_type + ' ' + dependent

                if dependent not in extracted_features:
                    extracted_features[dependent] = FeatureWord(dependent, features_modified=set(), sentences_from=set(), extracting_rules=set())
                    #print 'dependent has feature ' + ','.join(extracted_features[dependent].features_modified)

                extracted_features[dependent].sentences_from.add(hash_code)
                extracted_features[dependent].extracting_rules.add(1)
                #assert dependent in extracted_features
                extracted_sentiments[word].features_modified.add(dependent)  # Add new feature to set of features modified by opinion
                
                #for k,v in extracted_features.iteritems():
                #    for f in v.features_modified:
                #        if f not in extracted_features:
                #            print 'feature ' + f + ' missing from features_modified in ' + k

#    for k,v in extracted_sentiments.iteritems():
#        for f in v.features_modified:
#            if f not in extracted_features:
#                print 'feature ' + f + ' missing from features_modified in ' + k
# Not so sure about this rule
# O to T
# this rule is important to find many features
def rule_one_two(sentence_dependency_dict, extracted_features, extracted_sentiments):

    # for each sentence
    for hash_code in sentence_dependency_dict:
        sentence = sentence_dependency_dict[hash_code]
        # for each triple in that sentence
        for dependency in sentence:

            word = dependency[2][0].lower()  # O, given opinion word, like best
            dependency_type = dependency[1]  # O-Dep, like mod
            dependent = dependency[0][0].lower()  # H, like player

            # check if O is in the seed_opinion_set (which shall be enlarged after each iteration, or use extracted opinion instead).
            if word in extracted_sentiments and check_dependency(dependency_type, mr_list):

                # search dependent else where in the sentences with dependent as the head (H)
                second_dependency_list = dependencies_of_word(dependent, sentence)

                for second_dependency in second_dependency_list:

                    second_word = second_dependency[2][0].lower()  # T, target aspect to be added
                    second_dependency_type = second_dependency[1]  # T-Dep in MR

                    # check: a different second word is a noun and connected to H via a relationship in MR
                    if word != second_word and check_dependency(second_dependency_type, mr_list) and check_pos(
                            second_dependency[2][1], noun_list):

                        if second_word not in extracted_features:
                            extracted_features[second_word] = FeatureWord(second_word, features_modified=set(), sentences_from=set(), extracting_rules = set())
                        
                        extracted_features[second_word].sentences_from.add(hash_code)
                        extracted_features[second_word].extracting_rules.add(2)
                      
                        assert second_word in extracted_features
                        extracted_sentiments[word].features_modified.add(second_word)


# from T to O
# same as rule_one_one, but extract opinion given a target feature
# this rule is important, without which a lot of opinion can't be discovered.
def rule_two_one(sentence_dependency_dict, extracted_sentiments, extracted_features):
    for hash_code in sentence_dependency_dict:
        sentence = sentence_dependency_dict[hash_code]
        for dependency in sentence:

            word = dependency[2][0].lower()  # O, like good
            dependency_type = dependency[1]  # O-Dep in MR
            dependent = dependency[0][0].lower()  # T, like screen

            # the seed_feature_set shall be expanded after each iteration, or use extracted_features
            if dependent in extracted_features and check_dependency(dependency_type, mr_list) and check_pos(
                    dependency[2][1], adjective_list):
                # is extracted_sentiments the same as extracted opinions
                if word not in extracted_sentiments:
                    extracted_sentiments[word] = OpinionWord(word, features_modified=set(), sentiments_modified=set(),
                                                             sentences_from=set(), extracting_rules=set())
               
                assert dependent in extracted_features
                extracted_sentiments[word].features_modified.add(dependent)
                ###
                extracted_sentiments[word].sentences_from.add(hash_code)

                extracted_sentiments[word].extracting_rules.add(3)

# from T to O
def rule_two_two(sentence_dependency_dict, extracted_sentiments, extracted_features):
    for hash_code in sentence_dependency_dict:
        sentence = sentence_dependency_dict[hash_code]
        for dependency in sentence:

            word = dependency[2][0].lower()  # T like iPod
            dependency_type = dependency[1]  # T-Dep
            dependent = dependency[0][0].lower()  # H like player

            # seed_feature_set shall be expanding
            if word in extracted_features and check_dependency(dependency_type, mr_list):

                second_dependency_list = dependencies_of_word(dependent, sentence)

                for second_dependency in second_dependency_list:
                    second_word = second_dependency[2][0].lower()  # O
                    second_dependency_type = second_dependency[1]  # O-Dep

                    if word != second_word and check_dependency(second_dependency_type, mr_list) and check_pos(
                            second_dependency[2][1], adjective_list):
                        if second_word not in extracted_sentiments:
                            extracted_sentiments[second_word] = OpinionWord(second_word, features_modified = set(),
                                                                            sentiments_modified=set(), sentences_from=set(), extracting_rules = set())

                        assert word in extracted_features
                        extracted_sentiments[second_word].features_modified.add(word)
                        ###
                        extracted_sentiments[second_word].sentences_from.add(hash_code)
                        extracted_sentiments[second_word].extracting_rules.add(4)


# from T to T
def rule_three_one(sentence_dependency_dict, extracted_features):
    # return extracted_features, 0
    found_new = 0
    for hash_code in sentence_dependency_dict:
        sentence = sentence_dependency_dict[hash_code]
        for dependency in sentence:

            word_one = dependency[0][0].lower()  # Oij, like
            dependency_type = dependency[1]  # Oij-Dep
            word_two = dependency[2][0].lower()  # Oji

            if word_two in extracted_features and check_dependency(dependency_type, 'conj') and check_pos(
                    dependency[0][1], noun_list):
                if word_one not in extracted_features:
                    extracted_features[word_one] = FeatureWord(word_one, features_modified=set(), sentences_from=set(), extracting_rules = set())

                assert word_two in extracted_features
                extracted_features[word_one].features_modified.add(word_two)
                extracted_features[word_one].sentences_from.add(hash_code)

                extracted_features[word_one].extracting_rules.add(5)

            elif word_one in extracted_features and check_dependency(dependency_type, 'conj') and check_pos(
                    dependency[2][1], noun_list):
                if word_two not in extracted_features:
                    extracted_features[word_two] = FeatureWord(word_two, features_modified=set(), sentences_from=set(), extracting_rules = set())
                
                assert word_one in extracted_features
                extracted_features[word_two].features_modified.add(word_one)
                extracted_features[word_two].sentences_from.add(hash_code)
                
                extracted_features[word_two].extracting_rules.add(5)

# from T to T. For some reason it decreases precision
def rule_three_two(sentence_dependency_dict, extracted_features):
    for hash_code in sentence_dependency_dict:
        sentence = sentence_dependency_dict[hash_code]

        for dependency in sentence:
            word = dependency[2][0].lower()  # Oi
            dependency_type = dependency[1]  # Oi-Dep
            dependent = dependency[0][0].lower()  # H

            # similar issue for seed_feature_set
            if word in extracted_features:
                second_dependency_list = dependencies_of_word(dependent, sentence)

                for second_dependency in second_dependency_list:
                    second_word = second_dependency[2][0].lower()
                    # Sj-Dep                      Si-Dep                        Sj
                    if word != second_word and \
                            dependency_equivalent(second_dependency[1], dependency_type) and \
                            check_pos(second_dependency[2][1], noun_list):

                        if second_word not in extracted_features:
                            extracted_features[second_word] = FeatureWord(second_word, features_modified=set(), sentences_from=set(), extracting_rules = set())
                        
                        assert word in extracted_features
                        extracted_features[second_word].features_modified.add(word)
                        extracted_features[second_word].sentences_from.add(hash_code)
                        
                        extracted_features[second_word].extracting_rules.add(6)

# from O to O
def rule_four_one(sentence_dependency_dict, extracted_sentiments):
    found_new = 0
    for hash_code in sentence_dependency_dict:
        sentence = sentence_dependency_dict[hash_code]
        for dependency in sentence:
            word_one = dependency[0][0].lower()  # Oij
            dependency_type = dependency[1]  # Oij-Dep
            word_two = dependency[2][0].lower()  # Oji

            if word_two in extracted_sentiments and check_dependency(dependency_type, 'conj') and check_pos(
                    dependency[0][1], adjective_list):
                if word_one not in extracted_sentiments:
                    extracted_sentiments[word_one] = OpinionWord(word_one, features_modified = set(), sentiments_modified=set(), sentences_from=set(), extracting_rules = set())
                
                extracted_sentiments[word_one].sentiments_modified.add(word_two)
                ###
                extracted_sentiments[word_one].sentences_from.add(hash_code)
                extracted_sentiments[word_one].extracting_rules.add(7)

            elif word_one in extracted_sentiments and check_dependency(dependency_type, 'conj') and check_pos(
                    dependency[2][1], adjective_list):
                if word_two not in extracted_sentiments:
                    extracted_sentiments[word_two] = OpinionWord(word_two, features_modified = set(), sentiments_modified=set(), sentences_from=set(), extracting_rules = set())
                
                extracted_sentiments[word_two].sentiments_modified.add(word_one)
                ###
                extracted_sentiments[word_two].sentences_from.add(hash_code)
                extracted_sentiments[word_two].extracting_rules.add(7)


# from O to O
def rule_four_two(sentence_dependency_dict, extracted_sentiments):
    found_new = 0
    for hash_code in sentence_dependency_dict:
        sentence = sentence_dependency_dict[hash_code]
        for dependency in sentence:

            word = dependency[2][0].lower()  # Oi
            dependency_type = dependency[1]  # Oi-Dep
            dependent = dependency[0][0].lower()  # H

            # same issues regarding the seed_sentiment_set
            if word in extracted_sentiments:
                second_dependency_list = dependencies_of_word(dependent, sentence)

                for second_dependency in second_dependency_list:
                    
                    second_word = second_dependency[2][0].lower()
                    
                    if word != second_word and dependency_equivalent(second_dependency[1],
                                                                                 dependency_type) and check_pos(
                            second_dependency[2][1], adjective_list):

                        if second_word not in extracted_sentiments:
                            extracted_sentiments[second_word] = OpinionWord(second_word, features_modified = set(), sentiments_modified=set(),sentences_from=set(), extracting_rules = set())

                        extracted_sentiments[second_word].sentiments_modified.add(word)
                        ###
                        extracted_sentiments[second_word].sentences_from.add(hash_code)
                        extracted_sentiments[second_word].extracting_rules.add(8)

def dependency_equivalent(dependency_one, dependency_two):
    if dependency_one == dependency_two:
        return True
    elif check_dependency(dependency_one, mod_list):
        if check_dependency(dependency_two, subj_list):
            return True
        return False
    elif check_dependency(dependency_one, subj_list):
        if check_dependency(dependency_two, mod_list):
            return True
        return False
    return False


def dependencies_of_word(word, dependency_list):
    dependencies = []
    for dependency in dependency_list:
        if word == dependency[0][0]:
            dependencies.append(dependency)
    return dependencies


def check_dependency(to_check, desired_value):
    if type(desired_value) == list:
        if to_check in desired_value:
            return True
        return False
    if to_check == desired_value:
        return True
    return False


def check_pos(to_check, desired_value):
    if type(desired_value) == list:
        if to_check in desired_value:
            return True
        return False
    if to_check == desired_value:
        return True
    return False
