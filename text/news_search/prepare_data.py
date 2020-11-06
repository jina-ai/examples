__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import csv
import os
import re
import sys

csv.field_size_limit(sys.maxsize)


def read_data(data_fn, output_fn):
    _min_sent_len = 3
    _max_sent_len = 2000
    punct_chars = ['!', '.', '?', '։', '؟', '۔', '܀', '܁', '܂', '‼',
                   '‽', '⁇', '⁈', '⁉', '⸮', '﹖', '﹗', '！', '．', '？', '｡', '。']
    _slit_pat = re.compile('([{0}])+([^{0}])'.format(''.join(punct_chars)))
    _replace_pat = re.compile('{}'.format(punct_chars))

    if not os.path.exists(data_fn):
        print('file not found: {}'.format(data_fn))
    doc_list = []
    character_set = set()
    with open(data_fn, 'r') as f:
        f_h = csv.reader(f)
        for _idx, l in enumerate(f_h):
            if _idx == 0:
                continue
            _, description, tags = l

            tags = tags.strip('"')
            sents_str = _slit_pat.sub(r'\1\n\2', '{}\n'.format(tags))
            sents_str = sents_str.rstrip('\n')
            sents = [s.strip() for s in sents_str.split(
                '\n') if _min_sent_len <= len(s.strip()) <= _max_sent_len]
            character_set.add(description)
            for s in sents:
                doc_list.append('{}[SEP]{}'.format(description, s))
    doc_list = list(frozenset(doc_list))
    print('some statistics about the data:')
    print('\tnum characters: {}'.format(len(character_set)))
    print('\tnum documents: {}'.format(len(doc_list)))
    with open(output_fn, 'w') as f:
        f.write('\n'.join(doc_list))


if __name__ == '__main__':
    data_dir = 'tmp/jina/news'
    read_data(
        os.path.join(data_dir, 'bbc_news.csv'), os.path.join(data_dir, 'news_articles.csv'))
