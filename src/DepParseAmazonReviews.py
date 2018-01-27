"""
Warning: run this file in python3
"""

import requests
from multiprocessing import Pool
import time

default_config = {
    'server_address': 'http://localhost:9000',
    'ann': 'ssplit, tokenize, pos, depparse',
    'outputFormat': 'json'
}


def parse_reviews(input_file, output_file):
    """
    :param input_file:
    :param
    """
    input_file = open(input_file, 'r')
    rows = input_file.readlines()

    p = Pool(processes=8)
    parsed = p.map(_parse_one_row, rows)

    output_file = open(output_file, 'w')
    for p in parsed:
        output_file.write(p)
        output_file.write('\n')
    input_file.close()
    output_file.close()


def _parse_one_row(text):
    url = "%s?properties={'annotators': '%s', 'outputFormat':'%s'}" % (
        default_config['server_address'], default_config['ann'], default_config['outputFormat'])
    text = text.strip()
    hashval, review_txt = _get_hash_and_review(text)
    res = None
    while res is None:
        try:
            res = requests.post(url, data=review_txt)
        except Exception as e:
            print("while dep parsing: ", e)
            time.sleep(2)
    try:
        res = res.json(strict=False)
        parsed = _reformat_result(res)

        return "{} [{}]".format(hashval, parsed)
    except Exception as e:
        print("While parsing json:", e)
        return ""


def _reformat_result(json_rst):
    """ parse json result"""
    def _tostring(idx, tokens):
        if idx is 0:
            return "ROOT"
        else:
            return "{}/{}".format(tokens[idx-1]['word'], tokens[idx-1]['pos'])
    reformated_deps = []
    for s in json_rst['sentences']:
        tokens = s['tokens']
        deps = s['enhancedPlusPlusDependencies']
        for d in deps:
            gov = d['governor']
            dep = d['dependent']
            dep_str = "{}({}, {})".format(d['dep'], _tostring(gov, tokens), _tostring(dep, tokens))

            reformated_deps.append(dep_str)
    return ",".join(reformated_deps)

def _get_hash_and_review(t):
    """ get hash from review"""
    idx = t.index(' ')
    hashval = t[0:idx]

    rest = t[idx+1:]
    idx = rest.index(']')
    rest = rest[idx+1:]
    idx = rest.index(']')
    review_txt = rest[idx+2:]
    return hashval, review_txt

def main():
    """ modify default_config if needed"""
    reviews = [
        # {
        #     'input': '/home/zarzen/Dev/dprank/data/Cell_Phones_and_Accessories_id.txt',
        #     'output': '/home/zarzen/Dev/dprank/data/Cell_Phones_and_Accessories_parsed.txt'
        # },
        # {
        #     'input': '/home/zarzen/Dev/dprank/data/Electronics_id.txt',
        #     'output': '/home/zarzen/Dev/dprank/data/Electronics_parsed.txt'
        # },
        {
            'input': '/home/zarzen/Dev/dprank/data/Baby_id.txt',
            'output': '/home/zarzen/Dev/dprank/data/Baby_parsed.txt'
        },
        {
            'input': '/home/zarzen/Dev/dprank/data/Health_and_Personal_Care_id.txt',
            'output': '/home/zarzen/Dev/dprank/data/Health_and_Personal_Care_parsed.txt'
        },
        {
            'input': '/home/zarzen/Dev/dprank/data/Digital_Music_id.txt',
            'output': '/home/zarzen/Dev/dprank/data/Digital_Music_parsed.txt'
        }
    ]
    for r in reviews:
        parse_reviews(r['input'], r['output'])

if __name__ == "__main__":
    import sys
    if not sys.version_info >= (3, 5):
        print('Error: using python3.5 to run this file')
    else:
        main()
