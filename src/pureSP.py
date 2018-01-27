import re
from Config import get_config
config = get_config()




if __name__ == '__main__':

    centerfilename = [
        'Cell_Phones_and_Accessories',
        'Electronics',
        'Baby',
        'Health_and_Personal_Care',
        'Digital_Music']

    # centerfilename = ['Test']

    for i in centerfilename:

        hash = []
        for g in open(config.data_path + i + '/' + i + '_LP.txt'):
        # for g in open(config.data_path + i + '/' + 'All electronic productsknn_LP.txt'):
             hash.append(g.split(' ', 1)[0])
        print len(hash)

        sentence = []
        with open(config.data_path + i + '/' + i + '_SP_tagger.txt', 'r', )as file:
        # with open(config.data_path + i + '/' + 'All electronic productsknn_SP_tagger.txt', 'r', )as file:
            for line in file:
                l = line.split()
                m = []
                for part in l:
                    if part == 'X_NNP' or part == 'Y_NNP':
                        part = part[:1]
                    else:
                        part = part[part.index('_')+1:].strip()
                    m.append(part)
                sentence.append(' '.join(m))
            file.close()
        print len(sentence)

        with open(config.data_path + i + '/' + i + '_SP.txt', 'w', )as f:
        # with open(config.data_path + i + '/' +'All electronic productsknn_SP.txt', 'w', )as f:
            for m in range(len(hash)):
                f.write(hash[m]+' ')
                f.write(sentence[m]+'\n')
            f.close()