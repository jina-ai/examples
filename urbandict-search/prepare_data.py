__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import os
import zipfile
import csv
import json
from io import TextIOWrapper

MIN_UP_VOTES = 3
MIN_VOTES = 5
MIN_UP_DOWN_RATIO = 1.0
MIN_WORD_LENGTH = 2
MAX_WORD_LENGTH = 16


def main(root_path='/tmp'):
    # load the zip file and clean the data
    input_fn = 'urban-dictionary-words-dataset.zip'
    word_def_list = []
    input_path = os.path.join(root_path, input_fn)
    with zipfile.ZipFile(input_path) as z:
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
                if up_votes < MIN_UP_VOTES or (up_votes+down_votes) < MIN_VOTES or weight <= MIN_UP_DOWN_RATIO:
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
                word_def_list.append({'word': word, 'text': word_def, 'weight': weight})
    print('word_def size: {}/{}'.format(len(frozenset([w['word'] for w in word_def_list])), idx))
    print('definition size: {}/{}'.format(len(word_def_list), idx))

    # save the processed results
    output_dir = os.path.join(root_path, 'jina', 'urbandict')
    if not os.path.exists(output_dir):
        print('data output dir: {}'.format(output_dir))
        os.makedirs(output_dir, exist_ok=True)
    output_fn = 'urbandict-word-defs.json'
    output_path = os.path.join(output_dir, output_fn)
    with open(output_path, 'w') as f:
        json.dump(word_def_list, f, ensure_ascii=False, indent=4)
    print('processed data: {}'.format(output_path))


if __name__ == '__main__':
    main()
