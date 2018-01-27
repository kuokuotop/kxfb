class get_config():
    # path to word2vec binanry file
    #word2vec_path='/home/sihong/data/word2vec/GoogleNews-vectors-negative300.bin'
    
    # change the path to the stanford nlp packages when running on your machine
    stanford_pos_path = r'E:\tools\stanford_nlp\stanford-postagger-full-2017-06-09'
    stanford_core_path = r'E:\tools\stanford_nlp\stanford-corenlp-full-2016-10-31'
    stanford_parser_path = r'E:\tools\stanford_nlp\stanford-parser-full-2017-06-09'

    # path to data
    data_path = '../data/'
    file_names = ['Apex AD2600 Progressive-scan DVD player',
                  'Creative Labs Nomad Jukebox Zen Xtra 40GB',
                  'Nokia 6610',
                  'Canon G3',
                  'Nikon coolpix 4300',
                  'Cell_Phones_and_Accessories',
                  'Electronics',
                  'Baby',
                  'Health_and_Personal_Care',
                  'Digital_Music']

    manual_reviews = 'new_agreement.txt'
    dep_parsed_path = 'dep_parsed.pickle'
    amazon_review_path = '/home/sihong/data/amazon_reviews/'
    sentiment_seed = 'sentiment_seed.pickle'

    # path to result
    result_path = '../results/'
