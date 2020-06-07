__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import csv
import os
import re
import sys


def read_data(data_fn, output_fn):
    _min_sent_len = 3
    _max_sent_len = 64
    punct_chars = ['!', '.', '?', '։', '؟', '۔', '܀', '܁', '܂', '‼', '‽', '⁇', '⁈', '⁉', '⸮', '﹖', '﹗',
                   '！', '．', '？', '｡', '。']
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
            _, _, name, line = l
            line = line.strip('"')
            sents_str = _slit_pat.sub(r'\1\n\2', '{}\n'.format(line))
            sents_str = sents_str.rstrip('\n')
            sents = [s.strip() for s in sents_str.split('\n') if _min_sent_len <= len(s.strip()) <= _max_sent_len]
            character_set.add(name)
            name = _replace_pat.sub(r'', name)
            for s in sents:
                doc_list.append('{}[SEP]{}'.format(name, s))
    doc_list = list(frozenset(doc_list))
    print('some statistics about the data:')
    print('\tnum characters: {}'.format(len(character_set)))
    print('\tnum documents: {}'.format(len(doc_list)))
    with open(output_fn, 'w') as f:
        f.write('\n'.join(doc_list))


if __name__ == '__main__':
    data_dir = sys.argv[1]
    read_data(
        os.path.join(data_dir, 'All-seasons.csv'), os.path.join(data_dir, 'character-lines.csv'))
