import numpy
from Config import get_config
config = get_config()

def getlist(path):
    idStr_list = []
    pList = []
    with open(path, 'r') as f:
        for l in f:
            parts = l.split(',', 1)
            pList.append(parts[0])
            idStr_list.append(parts[1].strip())



    return idStr_list, pList

def getset(str):
    ID_set = set()
    for part in str.split():
        ID_set.add(part)
    return ID_set

if __name__ == '__main__':

    # centerfilename = [
    #     'Cell_Phones_and_Accessories',
    #     'Electronics',
    #     'Baby',
    #     'Health_and_Personal_Care',
    #     'Digital_Music']

    modes = ['LP', 'SP']
    # mode = ''

    # for i in xrange(2):
    #     mode = modes[i]
    #     for j in xrange(2, 12):
    #         n = j

            # PatternsPath = config.data_path + 'Test/' + 'Patterns_IDSET_' + str(n) + '_' + mode + '.txt'
    PatternsPath = config.data_path + 'Test/' + 'All electronic productsknn_Patterns_IDSET_0.003_LP.txt'
    PairsPath = config.data_path + 'Test/' + 'All electronic products_finalPairs_IDSET.txt'
    MatrixPath = config.data_path + 'Test/' + 'Matrix_'+str(0.003)+modes[0]+'.csv'

    pairID_str_list, pair_list = getlist(PairsPath)
    patternID_str_list, pattern_list = getlist(PatternsPath)

    a = numpy.zeros((len(pair_list), len(pattern_list)), dtype=numpy.int16)
    for m in pairID_str_list:
        Mnum = getset(m)
        for n in patternID_str_list:
            Nnum = getset(n)
            a[pairID_str_list.index(m)][patternID_str_list.index(n)] = len(Mnum & Nnum)
    print a

    numpy.savetxt(MatrixPath, a, fmt='%d', delimiter=',')
