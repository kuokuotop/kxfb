#!/usr/bin/python
import datetime
from Config import get_config
from SentencePruning import *

config = get_config()
# -*- coding: utf-8 -*-

class PrefixSpan:
    def __init__(self, g, sentences, sequences, minSupport=0.1, maxPatternLength=10):

        minSupport = minSupport * len(sequences)
        self.PLACE_HOLDER = '_'

        freqSequences = self._prefixSpan(
            self.SequencePattern([], None, maxPatternLength, self.PLACE_HOLDER),
            sequences, minSupport, maxPatternLength,  sentences, g)

        self.freqSeqs = PrefixSpan.FreqSequences(freqSequences)

    @staticmethod
    def train(g, sentences, sequences, minSupport=0.1, maxPatternLength=10):
        return PrefixSpan(g, sentences, sequences, minSupport, maxPatternLength)

    def freqSequences(self):
        return self.freqSeqs

    class FreqSequences:
        def __init__(self, fs):
            self.fs = fs

        def collect(self):
            return self.fs

    class SequencePattern:
        def __init__(self, sequence, support, maxPatternLength, place_holder):
            self.place_holder = place_holder
            self.sequence = []
            for s in sequence:
                self.sequence.append(list(s))
            self.freq = support

        def append(self, p):
            if p.sequence[0][0] == self.place_holder:
                first_e = p.sequence[0]
                first_e.remove(self.place_holder)
                self.sequence[-1].extend(first_e)
                self.sequence.extend(p.sequence[1:])
            else:
                self.sequence.extend(p.sequence)
                if self.freq is None:
                    self.freq = p.freq
            self.freq = min(self.freq, p.freq)

    def _checkPatternLengths(self, pattern, maxPatternLength):
        for s in pattern.sequence:
            if len(s) > maxPatternLength:
                return False
        return True

    def _prefixSpan(self, pattern, S, threshold, maxPatternLength, sentences, g):
        patterns = []
        if self._checkPatternLengths(pattern, maxPatternLength):
            f_list = self._frequent_items(S, pattern, threshold, maxPatternLength)
            for i in f_list:
                sign = 0
                # print 'f_list i:', i.sequence
                p = self.SequencePattern(pattern.sequence, pattern.freq, maxPatternLength, self.PLACE_HOLDER)
                # p.append(i)
                # ------------------------------------
                if p.sequence == []:
                    p.append(i)
                    sign = 1
                else:
                    sup = 0
                    p_str =''
                    for word_list in p.sequence:
                        p_str += word_list[0]+' '
                    p_str = p_str.strip()
                    # print p_str
                    idSet = orderedpatternid(p_str, sentences)
                    # print idSet
                    for sentenPruning in idSet:
                        pruningS = sentences[sentenPruning.sentenceId]\
                            .split()[sentenPruning.pruningIndex:sentenPruning.pruningIndex+g+1]
                        for word in pruningS:
                            if i.sequence[0][0] == word:
                                sup += 1
                                break
                    # print '++++++++++', sup,g
                    if sup >=threshold :
                        # print '______'
                        i.frep = sup
                        p.append(i)
                        sign = 1
                # ------------------------------------
                # for m in patterns:
                #     print 'pattern element:', m.sequence
                # if self._checkPatternLengths(pattern, maxPatternLength):
                if sign == 1:
                    patterns.append(p)
                    p_S = self._build_projected_database(S, p)
                    p_patterns = self._prefixSpan(p, p_S, threshold, maxPatternLength, sentences, g)
                    patterns.extend(p_patterns)
        return patterns

    def _frequent_items(self, S, pattern, threshold, maxPatternLength):
        items = {}
        _items = {}
        f_list = []
        if S is None or len(S) == 0:
            return []

        if len(pattern.sequence) != 0:
            last_e = pattern.sequence[-1]
        else:
            last_e = []

        for s in S:
            if s==[]:
                continue
            # class 1
            is_prefix = True
            for item in last_e:
                if item not in s[0]:
                    is_prefix = False
                    break
            if is_prefix and len(last_e) > 0:
                index = s[0].index(last_e[-1])
                if index < len(s[0]) - 1:
                    for item in s[0][index + 1:]:
                        if item in _items:
                            _items[item] += 1
                        else:
                            _items[item] = 1

            # class 2
            # print s
            # print s[0]
            if self.PLACE_HOLDER in s[0]:
                for item in s[0][1:]:
                    # print '==============='
                    if item in _items:
                        _items[item] += 1
                    else:
                        _items[item] = 1
                s = s[1:]
            # print _items

            # class 3
            counted = []
            for element in s:
                for item in element:
                    if item not in counted:
                        counted.append(item)
                        if item in items:
                            items[item] += 1
                        else:
                            items[item] = 1

        f_list.extend([self.SequencePattern([[self.PLACE_HOLDER, k]], v, maxPatternLength, self.PLACE_HOLDER)
                       for k, v in _items.iteritems()
                       if v >= threshold])
        # for i in f_list:
        #     print '=======',i.sequence
        f_list.extend([self.SequencePattern([[k]], v, maxPatternLength, self.PLACE_HOLDER)
                       for k, v in items.iteritems()
                       if v >= threshold])

        # todo: can be optimised by including the following line in the 2 previous lines
        f_list = [i for i in f_list if self._checkPatternLengths(i, maxPatternLength)]

        sorted_list = sorted(f_list, key=lambda p: p.freq)
        return sorted_list

    def _build_projected_database(self, S, pattern):
        """
        suppose S is projected database base on pattern's prefix,
        so we only need to use the last element in pattern to
        build projected database
        """
        p_S = []
        last_e = pattern.sequence[-1]
        last_item = last_e[-1]
        for s in S:
            p_s = []
            for element in s:
                is_prefix = False
                if self.PLACE_HOLDER in element:
                    if last_item in element and len(pattern.sequence[-1]) > 1:
                        is_prefix = True
                else:
                    is_prefix = True
                    for item in last_e:
                        if item not in element:
                            is_prefix = False
                            break

                if is_prefix:
                    e_index = s.index(element)
                    i_index = element.index(last_item)
                    if i_index == len(element) - 1:
                        p_s = s[e_index + 1:]
                    else:
                        p_s = s[e_index:]
                        index = element.index(last_item)
                        e = element[i_index:]
                        e[0] = self.PLACE_HOLDER
                        p_s[0] = e
                    break
            if len(p_s) != 0:
                p_S.append(p_s)
        return p_S

def read(filename, g, G, L):
    S = []
    sentences = []
    review = {}
    hash_index = []
    with open(filename, 'r') as input:
        for line in input.readlines():
            elements = line.split(' ', 1)
            hash_index.append(elements[0])
            # sentence_str = elements[1].strip().strip('.').strip()
            sentence_str = elements[1].replace('.', '').replace('  ', ' ').strip('\n').strip()

            Xindex = -1
            Yindex = -1
            count = 0
            sentence_list = sentence_str.split()
            for xy in sentence_list:
                if 'X'==xy and count==0:
                    count = 1
                    Xindex = sentence_list.index(xy)
                if 'Y'==xy:
                    Yindex = sentence_list.index(xy)
            if Xindex <= Yindex:
                m = Xindex - 7 if Xindex - 7>0 else 0
                n = Yindex + 7 if Xindex + 7<len(sentence_list)-1 else len(sentence_list)
            else:
                m = Yindex - 7 if Yindex - 7 > 0 else 0
                n = Xindex + 7 if Xindex + 7 < len(sentence_list) - 1 else len(sentence_list)
            sentence_list = sentence_list[m:n]
            sentence_str = ' '.join(sentence_list)
            # print sentence_str
            sentences.append(sentence_str)
            # print sentence_str
            # review[elements[0]] = elements[1].replace('.', '').replace('  ', ' ').strip('\n').strip()
            words = sentence_str.split()

            # words = review[elements[0]].split()
            temp = []
            for ele in words:
                temp.append(ele.split())
            S.append(temp)
        print len(sentences)
    return S, sentences, hash_index


# only X Y
def selecting(patterns):
    newpatterns = []
    patternset=set()
    for part in patterns:
        str =''
        coutX = 0
        coutY = 0
        for word in part.sequence:
            if word[0] == 'X':
                coutX += 1
            if word[0] == 'Y':
                coutY += 1
            str += ''.join(word)+' '
        if coutX == 1 and coutX == coutY and len(part.sequence)<=5:
            # newpatterns.append(str)
            str = str.strip()
            patternset.add(str)
    for i in patternset:
        print i
    newpatterns = list(patternset)

    return newpatterns


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
        senPruning = SentencePruning(sentenceId, pruningIndex)
        # print index
        if(senPruning.sentenceId!= -1):
            idSet.add(senPruning)
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

    # centerfilename = [
    #     'Cell_Phones_and_Accessories',
    #     'Electronics',
    #     'Baby',
    #     'Health_and_Personal_Care',
    #     'Digital_Music']

    centerfilename = ['Test']

    modes = ['LP',
            'SP']
    # modes = ['LP']

    g = 2
    G = 4
    L = 5

    for i in xrange(1):
        print i
        f = centerfilename[i]
        for mode in modes:
            mode = 'SP'
            # SPpath = config.data_path + f + '/' + f + '_' + mode + '.txt'
            SPpath = config.data_path + f + '/' + 'All electronic productsknn_' + mode + '.txt'
            # SPpath = config.data_path + 'Test' + '/' + 'All electronic products_LP.txt '
            for n in xrange(3, 4):
                print n
                m = n/1000.
                print m

                stime = datetime.datetime.now()
                S, sentences, hashAndIndex = read(SPpath, g, G, L)
                # print S
                # print sentences
                etime = datetime.datetime.now()
                print 'read       time', (etime - stime).seconds


                stime = datetime.datetime.now()
                model = PrefixSpan.train(g, sentences, S, minSupport=m, maxPatternLength=5)
                result = model.freqSequences().collect()
                etime = datetime.datetime.now()
                print 'generation time', (etime - stime).seconds

                for fs in result:
                    print('{}, {}'.format(fs.sequence, fs.freq))

                # selected
                stime = datetime.datetime.now()
                newPatterns = selecting(result)
                etime = datetime.datetime.now()
                print 'selected   time', (etime - stime).seconds

                # print 'newPatterns:\n',newPatterns

                # print hashAndIndex
                stime = datetime.datetime.now()
                PIDSETpath = config.data_path + f + '/' + 'All electronic productsknn' + '_' + 'Patterns_IDSET_' + str(m) + '_' + mode + '.txt'
                # print PIDSETpath
                with open(PIDSETpath, 'w') as f:
                    for pattern in newPatterns:
                        f.write(pattern.strip() + ',')
                        # print orderedpatternid(pattern, sentences)
                        for s in orderedpatternid(pattern, sentences):
                            f.write(hashAndIndex[s.sentenceId] + ' ')
                        f.write('\n')
                    f.close()
                etime = datetime.datetime.now()
                print 'write     time', (etime - stime).seconds


