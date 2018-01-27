#-*-coding:utf-8 -*-
from Config import get_config
config = get_config()

# #   799 all
# alllabelPath = config.data_path + '/knn' + '/' + 'dp_produced_pairs.txt'
# f = open(alllabelPath, 'rU')
# alllabel = set()
# for line in f:
# 	alllabel.add(line.strip('\n'))
# f.close()
# print len(alllabel)


#   703  positive


def orderedpatternid(pattern, sentences):
    # print sentences
    idSet = set()
    # print 'jkjk',pattern
    patternlist = pattern.split()
    for sentence in sentences:
        # print '------------------------sentence Bengin-------------------------'
        # print patternlist
        # print sentence
        sentencelist = sentence.split()
        # print getid(patternlist, sentencelist, sentence, sentences)
        sentenceId, pruningIndex = getid(patternlist, sentencelist, sentence, sentences)
        # print index
        if(sentenceId!= -1):
            idSet.add(sentenceId)
        # print idSet
        # print '------------------------sentence END-------------------------'
    return idSet

def getid(patternlist, sentencelist ,sentence ,sentences):

    if patternlist == []:
        return -1, -1

    if sentencelist == []:
        return -1, -1

    for Pwordstr in patternlist:
        # print type(Pwordstr)
        for Swordstr in sentencelist:
            # print Swordstr
            if Pwordstr == Swordstr:
                # print  Swordstr , Pwordstr
                indexP = patternlist.index(Pwordstr)+1
                # print indexP
                indexS = sentencelist.index(Swordstr)+1
                # print indexS
                if patternlist.index(Pwordstr) == patternlist.index(patternlist[-1]):
                    # print '+++++++++++++++++++++',indexS
                    return sentences.index(sentence), indexS
                patternlist = patternlist[indexP:]
                sentencelist = sentencelist[indexS:]
                # print patternlist
                # print sentencelist
                return getid(patternlist, sentencelist, sentence, sentences)

        return -1, -1

if __name__ == "__main__":

    #   703 positive pairs
    pospairsPath = config.data_path + '/knn' + '/' + 'labeled_pairs.txt'
    f = open(pospairsPath, 'rU')
    pospairs = set()
    for line in f:
        pospairs.add(line.strip('\n'))
    f.close()
    print len(pospairs)

    #   903   pairs
    pairPath = config.data_path + '/Test' + '/' + 'All electronic products_Pairs_IDSET.txt'
    f = open(pairPath, 'rU')
    pairs = set()
    dict = {}
    for line in f:
        parts = line.split(',', 1)
        dict[parts[0]] = parts[1]
        pairs.add(parts[0])
    f.close()

    finalpairs = pospairs | pairs
    print len(finalpairs)

    sentences = []
    hashAndIndex = []
    with open(config.data_path + 'All electronic products_id.txt', 'r', )as file:
        for line in file:
            parts = line.split(' ', 1)
            sentences.append(parts[1])
            hashAndIndex.append(parts[0])
        file.close()

    count = 0
    finaldict = {}
    for pair in finalpairs:
        # pair_ = ','.join(pair.split(' '))
        if pair in dict.keys():
            finaldict[pair] = dict[pair].strip('\n')
        else:
            hashset = set()
            for index in orderedpatternid(pair, sentences):
                hashset.add(hashAndIndex[index])
            if len(hashset) == 0:
                continue
            finaldict[pair] = ' '.join(hashset).strip('\n')

    label = []
    with open(config.data_path + 'Test/' + 'All electronic products_finalPairs_IDSET.txt', 'w', )as f:
        for a in finaldict.keys():
            if a in pospairs:
                print a
                label.append(1)
            else:
                print '+++', a
                label.append(0)
            f.write(a+',')
            f.write(finaldict[a]+'\n')
        f.close()

    with open(config.data_path + 'Test/' + 'All electronic products_label.txt', 'w', )as f:
        for a in label:
            f.write(str(a))
            f.write('\n')
        f.close()

    with open(config.data_path + 'Test/' + 'All electronic products_finalPairs.txt', 'w', )as f:
        for a in finaldict.keys():
            for b in finaldict[a].split():
                f.write(b+' ')
                f.write(','.join(a.split())+'\n')
        f.close()

'''
    #   903*x feature of dict
    Path = config.data_path + '/Test' + '/' + 'Matrix_11LP.csv'#ourmatrix
    f = open(Path, 'rU')
    allSample = {}
    i = 0
    for line in f:
        # print pairs[i]
        allSample[pairs[i]] = line
        i += 1
    f.close()
    
    # print set(pairs)
    # print poslabel
    poslabeledPairs = set(pairs) & poslabel
    # print poslabeledPairs
    neglabeledPairs = set(pairs) & (alllabel - poslabel)
    print len(alllabel), len(poslabel)
    print len(alllabel - poslabel)
    poslabeledSample = {}
    poslabeledPairs = list(poslabeledPairs)
    print poslabeledPairs
    for pair in poslabeledPairs:
        poslabeledSample[pair] = allSample[pair]
    neglabeledSample = {}
    neglabeledPairs = list(neglabeledPairs)
    for pair in neglabeledPairs:
        neglabeledSample[pair] = allSample[pair]
    
    print poslabeledSample
    print '++++++++++++++++++++++++++++++++++++', len(poslabeledSample)
    print neglabeledSample
    print '++++++++++++++++++++++++++++++++++++', len(neglabeledSample)
'''