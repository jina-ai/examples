"""Helper functions for the multires example"""

import csv
import itertools as it
import os

from jina import Document


def input_generator(num_docs: int):
    lyrics_file = os.environ.setdefault(
        'JINA_DATA_PATH', 'toy-data/lyrics-toy-data1000.csv'
    )
    with open(lyrics_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in it.islice(reader, num_docs):
            if row[-1] == 'ENGLISH':
                with Document() as d:
                    d.tags['ALink'] = row[0]
                    d.tags['SName'] = row[1]
                    d.tags['SLink'] = row[2]
                    d.text = row[3]
                    yield d
