import string
from Config import get_config
config = get_config()


def substitution(input_pairsfile, input_idfile, output_filename):
    pruninglist = pruningdata(input_idfile)
    a = set()
    with open(input_pairsfile, 'r', ) as f:
        for line in f:
            # print line
            parts = line.split(' ', 1)
            a.add(parts[0])
            pair = parts[1].split(',')
            pair[1] = pair[1].strip()
            pruninglist[parts[0]] = pruninglist[parts[0]].replace(' '+pair[0]+' ', ' X ').replace(' '+pair[1]+' ', ' Y ').strip()
        f.close()

    with open(output_filename, 'w') as file:
        for hash in a:
            file.write(hash+' ')
            file.write(pruninglist[hash]+' .\n')
        file.close()


def pruningdata(input_idfile):
    pruninglist={}
    with open(input_idfile, 'r', ) as f:
        for line in f:
            parts = line.split(' ', 1)
            parts[1] = parts[1][parts[1].rindex('[')+3:].translate(None, string.punctuation).strip().lower()
            pruninglist[parts[0]] = ' '+parts[1]+' '
        f.close()
    return pruninglist

if __name__ == '__main__':
    # f=config.file_names[1]
    # substitution(config.data_path + f + '_pairs.txt', config.data_path + f + '_id.txt', config.data_path + f + '_sub.txt')

    centerfilename = [
        'Cell_Phones_and_Accessories',
        'Electronics',
        'Baby',
        'Health_and_Personal_Care',
        'Digital_Music']

    for i in xrange(0, 5):
        f = centerfilename[i]
        print f
        substitution(config.data_path + f +'/' + f + '_pairs_removed.txt', config.data_path +f +'/'+ f + '_id.txt', config.data_path +f +'/'+ f + '_LP.txt')

    # with open(config.data_path + 'All electronic products_LP.txt', 'w', )as file:
    #     for i in xrange(0, 5):
    #         f = config.file_names[i]
    #         for line in open(config.data_path + f + '_sub.txt'):
    #             # part = line.split(' ', 1)
    #             file.writelines(line)
    #         # file.write('\n')
    #     file.close()
    # f = 'Test'
    # substitution(config.data_path + f +'/' + 'All electronic products_finalPairs.txt', config.data_path +f +'/'+ 'All electronic products' + '_id.txt', config.data_path +f +'/'+ 'All electronic products' + 'knn_LP.txt')
