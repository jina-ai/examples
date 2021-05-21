import os
import sys

import copy
import mmap
import numpy as np
from pathlib import Path
from typing import Optional, Iterable, Dict, List, Tuple

from jina import Document, requests, Executor, DocumentArray

from jina.logging import JinaLogger

from jina.helper import get_readable_size

HEADER_NONE_ENTRY = (-1, -1, -1)

BYTE_PADDING = 4
logger = JinaLogger(__name__)

class NumpyIndexer(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._docs = DocumentArray()

    @requests(on='/index')
    def index(self, docs: 'DocumentArray', **kwargs):
        self._docs.extend(docs)


    @requests(on='/search')
    def search(self, docs: 'DocumentArray', parameters: Dict = None, **kwargs):
        if parameters is None:
            parameters = {'top_k': 5}

        doc_embeddings = np.stack(docs.get_attributes('embedding'))
        q_emb = _ext_A(_norm(doc_embeddings))
        d_emb = _ext_B(_norm(self._docs.get_attributes('embedding')))
        dists = _cosine(q_emb, d_emb)
        positions, dist = self._get_sorted_top_k(dists, int(parameters['top_k']))
        for _q, _positions, _dists in zip(docs, positions, dist):
            for position, _dist in zip(_positions, _dists):
                d = Document(self._docs[int(position)])
                d.score.value = 1 - _dist
                _q.matches.append(d)

    @staticmethod
    def _get_sorted_top_k(
        dist: 'np.array', top_k: int
    ) -> Tuple['np.ndarray', 'np.ndarray']:
        if top_k >= dist.shape[1]:
            idx = dist.argsort(axis=1)[:, :top_k]
            dist = np.take_along_axis(dist, idx, axis=1)
        else:
            idx_ps = dist.argpartition(kth=top_k, axis=1)[:, :top_k]
            dist = np.take_along_axis(dist, idx_ps, axis=1)
            idx_fs = dist.argsort(axis=1)
            idx = np.take_along_axis(idx_ps, idx_fs, axis=1)
            dist = np.take_along_axis(dist, idx_fs, axis=1)

        return idx, dist
    
def _get_ones(x, y):
    return np.ones((x, y))

def _ext_A(A):
    nA, dim = A.shape
    A_ext = _get_ones(nA, dim * 3)
    A_ext[:, dim : 2 * dim] = A
    A_ext[:, 2 * dim :] = A ** 2
    return A_ext

def _ext_B(B):
    nB, dim = B.shape
    B_ext = _get_ones(dim * 3, nB)
    B_ext[:dim] = (B ** 2).T
    B_ext[dim : 2 * dim] = -2.0 * B.T
    del B
    return B_ext

def _euclidean(A_ext, B_ext):
    sqdist = A_ext.dot(B_ext).clip(min=0)
    return np.sqrt(sqdist)

def _norm(A):
    return A / np.linalg.norm(A, ord=2, axis=1, keepdims=True)

def _cosine(A_norm_ext, B_norm_ext):
    return A_norm_ext.dot(B_norm_ext).clip(min=0) / 2