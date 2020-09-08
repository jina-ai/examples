__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import zipfile
import csv
from io import TextIOWrapper

MIN_UP_VOTES = 3
MIN_VOTES = 5
MIN_UP_DOWN_RATIO = 1.0
MIN_WORD_LENGTH = 2
MAX_WORD_LENGTH = 16


def main(input_fn, output_fn):
    # load the zip file and clean the data
    word_def_list = []
    with zipfile.ZipFile(input_fn) as z:
        with z.open('urbandict-word-defs.csv', 'r') as f:
            r = csv.reader(TextIOWrapper(f, 'utf-8'))
            for idx, l in enumerate(r):
                if idx == 0:  # skip the header
                    num_cols = len(l)
                    continue
                if len(l) != num_cols:  # drop the empty lines
                    continue
                _, word, up_votes, down_votes, _, word_def = l
                up_votes = int(up_votes)
                down_votes = int(down_votes)
                weight = up_votes * 1.0 / down_votes if down_votes != 0 else up_votes
                if len(word_def) == 0:
                    # filter out the empty definitions
                    continue
                if up_votes < MIN_UP_VOTES or (up_votes + down_votes) < MIN_VOTES or weight <= MIN_UP_DOWN_RATIO:
                    # filter out the entries that have too few up-votes
                    continue
                if len(word) < MIN_WORD_LENGTH or len(word) > MAX_WORD_LENGTH:
                    # filter out the entries that are too short or too long
                    continue
                if not word:
                    # filter out the empty entries
                    continue
                word = word.lower().strip()  # convert the words into the lower case
                word_def = word_def.lower().strip()
                word_def_list.append('{}+-={}'.format(word, word_def))  # '+-=' for unique seperation
    print('{} definitions are kept out of {} after washing'.format(len(word_def_list), idx))
    with open(output_fn, 'w') as f:
        f.write('\n'.join(word_def_list))
    print('processed data: {}'.format(output_fn))


if __name__ == '__main__':
    work_dir = '/tmp/jina/urbandict'
    if not os.path.exists(work_dir):
        print('working directory: {}'.format(work_dir))
        os.makedirs(work_dir, exist_ok=True)
    input_fn = os.environ.get('RAW_DATA_DIR', '/tmp/urban-dictionary-words-dataset.zip')
    output_fn = os.environ.get('WASHED_DATA_DIR', os.path.join(work_dir, 'urbandict-word-defs.csv'))

    main(input_fn, output_fn)
