"""
Extract reviews from amazon dataset(unlabled)
"""
import gzip
import re
from hashlib import md5

def _review_reader(filepath):
    gz = gzip.open(filepath)
    for l in gz:
        yield eval(l)


def _add_whitespace(text):
    """ Add white space for sentence splitting

    Some reviews has follow issue:
    'This review is tailed with another.Another review here cannot be
    separated by sent-tokenizer.'

    DONE add white space for a!W a?W

    Args:
      text: string contains reviews
    Returns:
      String added white space for separation.
    """
    reg = r'([a-z]*[a-z])([\.\!\?])([A-Za-z][a-z]*\ )'
    # for debugging
    # matched = re.findall(reg, text)
    # print("matched: ", len(matched))
    # print(matched[0:20])
    return re.sub(reg, r'\1\2 \3', text)

def extract_unlabeled_reviews(output_file, input_file, n):
    """ input amazon reviews gzip file
    output plain text
    :param n: needed reviews
    """
    reviews = _review_reader(input_file)
    output_file = open(output_file, 'w')
    for i in range(n):
        r = next(reviews)
        text = r['reviewText']
        text = _add_whitespace(text)
        hashval = md5(text.encode('utf-8')).hexdigest()
        output_file.write("{} [],[],{}\n".format(hashval, text))
    output_file.close()


def main():
    """
    modify amazon_reviews before run
    """
    amazon_reviews = [
        {
            'input': '/home/zarzen/Dev/relationembeddings/data/pre_train/reviews_Cell_Phones_and_Accessories_5.json.gz',
            'output': '/home/zarzen/Dev/dprank/data/Cell_Phones_and_Accessories_id.txt',
            'n': 50000
        },
        {
            'input': '/home/zarzen/Dev/relationembeddings/data/pre_train/reviews_Electronics_5.json.gz',
            'output': '/home/zarzen/Dev/dprank/data/Electronics_id.txt',
            'n': 50000
        },
        {
            'input': '/home/zarzen/Dev/relationembeddings/data/pre_train/reviews_Baby_5.json.gz',
            'output': '/home/zarzen/Dev/dprank/data/Baby_id.txt',
            'n':50000
        },
        {
            'input': '/home/zarzen/Dev/relationembeddings/data/pre_train/reviews_Health_and_Personal_Care_5.json.gz',
            'output': '/home/zarzen/Dev/dprank/data/Health_and_Personal_Care_id.txt',
            'n': 50000
        },
        {
            'input': '/home/zarzen/Dev/relationembeddings/data/pre_train/reviews_Digital_Music_5.json.gz',
            'output': '/home/zarzen/Dev/dprank/data/Digital_Music_id.txt',
            'n': 50000
        }

        ]
    for reviews in amazon_reviews:
        extract_unlabeled_reviews(reviews['output'], reviews['input'], reviews['n'])

if __name__ == "__main__":
    main()
