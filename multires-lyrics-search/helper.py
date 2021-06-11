"""Helper functions for the multires example"""

import csv
import itertools as it
import os
import numpy as np

from jina import Document


def input_generator(num_docs: int):
    lyrics_file = os.environ.setdefault('JINA_DATA_FILE',
                                        'lyrics-data/lyrics-toy-data1000.csv')
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


def num_input_docs():
    lyrics_file = os.environ.setdefault(
        'JINA_DATA_PATH', 'lyrics-data/lyrics-toy-data1000.csv'
    )
    with open(lyrics_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        return len(list(reader))

def _ext_A(A):
    nA, dim = A.shape
    A_ext = np.ones((nA, dim * 3))
    A_ext[:, dim : 2 * dim] = A
    A_ext[:, 2 * dim :] = A ** 2
    return A_ext


def _ext_B(B):
    nB, dim = B.shape
    B_ext = np.ones((dim * 3, nB))
    B_ext[:dim] = (B ** 2).T
    B_ext[dim : 2 * dim] = -2.0 * B.T
    del B
    return B_ext


def _norm(A):
    return A / np.linalg.norm(A, ord=2, axis=1, keepdims=True)


def _euclidean(A_ext, B_ext):
    sqdist = A_ext.dot(B_ext).clip(min=0)
    return np.sqrt(sqdist)