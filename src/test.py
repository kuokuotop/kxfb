from SentencePruning import *
from Config import get_config
import string
config = get_config()
# a = set()
# b = SentencePruning(3, 2)
# a.add(b)
# for i in a:
#     print i.sentenceId
#     print i.pruningIndex
# for n in xrange(60, 10, 10):
#     print n
#     m = n / 1000.
#     print m
# print a

def pruningdata(input_idfile):
    # pruningdict={}
    pruninglist = []
    with open(input_idfile, 'r', ) as f:
        for line in f:
            parts = line.split(' ', 1)
            parts[1] = parts[1][parts[1].rindex('[')+3:].translate(None, string.punctuation).strip().lower()
            pruninglist.append(' '.join(parts))
            # pruningdict[parts[0]] = parts[1]
        f.close()
    return pruninglist

with open(config.data_path + 'All electronic products_id.txt', 'w', )as file:
    for i in xrange(0, 5):
        f = config.file_names[i]
        pruninglist = pruningdata(config.data_path + f + '_id.txt')
        for line in pruninglist:
            # part = line.split(' ', 1)
            file.write(line+'\n')
            # file.write('\n')
    file.close()

# with open(config.data_path + 'Test/' + 'All electronic products_id.txt', 'w', )as file:
#     for i in xrange(0, 5):
#         f = config.file_names[i]
#         for line in open(config.data_path + f + '_id.txt'):
#             # part = line.split(' ', 1)
#             file.writelines(line)
#         # file.write('\n')
#     file.close()
