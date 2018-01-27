from ReviewParser import *

from Config import get_config
config = get_config()

from hashlib import md5

def Bing2MyFormat(input_filename, output_filename):
    """
        Transform Bing Liu's product review text datasets to my format, with each line being:
            ID, feature_list, opinion_list, sentence
    """
    review_list = load_reviews(input_filename)
    with open(output_filename, 'w') as f:
        # every annotatedReview
        for r in review_list:
            f.write(md5(r.sentence.encode('utf-8')).hexdigest() + ' ')
            f.write('[' + ','.join(r.feature_list) +'],')
            f.write('[' + ','.join(r.opinion_list) +'],')
            f.write(r.sentence + '\n')
        f.close()

if __name__ == '__main__':
    for f in config.file_names:
        # transform bing's dataset to my format
        Bing2MyFormat(config.data_path + f + '.txt', config.data_path + f + '_id.txt')

        # load the records (id, features, opinions, sentence)
        # review_list = load_manual_reviews(config.data_path + f + '_id.txt')
        #print get_features_from_reviews(review_list)
        #print get_opinions_from_reviews(review_list)
        #print get_hash_from_reviews(review_list)

        # test loading parsed results
        #id_dependencies = load_id_dependencies(config.data_path + f + '_parsed.txt')
