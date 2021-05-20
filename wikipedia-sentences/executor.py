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

def import_vectors(path: str, pea_id: str):
    """Import id and vectors
    :param path: the path to the dump
    :param pea_id: the id of the pea (as part of the shards)
    :return: the generators for the ids and for the vectors
    """
    logger.info(f'Importing ids and vectors from {path} for pea_id {pea_id}')
    path = os.path.join(path, pea_id)
    ids_gen = _ids_gen(path)
    vecs_gen = _vecs_gen(path)
    return ids_gen, vecs_gen

def import_metas(path: str, pea_id: str):
    """Import id and metadata
    :param path: the path of the dump
    :param pea_id: the id of the pea (as part of the shards)
    :return: the generators for the ids and for the metadata
    """
    logger.info(f'Importing ids and metadata from {path} for pea_id {pea_id}')
    path = os.path.join(path, pea_id)
    ids_gen = _ids_gen(path)
    metas_gen = _metas_gen(path)
    return ids_gen, metas_gen


def _ids_gen(path: str):
    with open(os.path.join(path, 'ids'), 'r') as ids_fh:
        for l in ids_fh:
            yield l.strip()

def _vecs_gen(path: str):
    with open(os.path.join(path, 'vectors'), 'rb') as vectors_fh:
        while True:
            next_size = vectors_fh.read(BYTE_PADDING)
            next_size = int.from_bytes(next_size, byteorder=sys.byteorder)
            if next_size:
                vec = np.frombuffer(
                    vectors_fh.read(next_size),
                    dtype=DUMP_DTYPE,
                )
                yield vec
            else:
                break

def _metas_gen(path: str):
    with open(os.path.join(path, 'metas'), 'rb') as metas_fh:
        while True:
            next_size = metas_fh.read(BYTE_PADDING)
            next_size = int.from_bytes(next_size, byteorder=sys.byteorder)
            if next_size:
                meta = metas_fh.read(next_size)
                yield meta
            else:
                break

class _WriteHandler:
    """
    Write file handler.
    :param path: Path of the file.
    :param mode: Writing mode. (e.g. 'ab', 'wb')
    """

    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
        self.body = open(self.path, self.mode)
        self.header = open(self.path + '.head', self.mode)

    def __enter__(self):
        if self.body.closed:
            self.body = open(self.path, self.mode)
        if self.header.closed:
            self.header = open(self.path + '.head', self.mode)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()

    def close(self):
        """Close the file."""
        if not self.body.closed:
            self.body.close()
        if not self.header.closed:
            self.header.close()

    def flush(self):
        """Clear the body and header."""
        if not self.body.closed:
            self.body.flush()
        if not self.header.closed:
            self.header.flush()

class FileWriterMixin:
    """Mixing for providing the binarypb writing and reading methods"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start = 0
        self._page_size = mmap.ALLOCATIONGRANULARITY

    def get_add_handler(self) -> '_WriteHandler':
        """
        Get write file handler.
        :return: write handler
        """
        # keep _start position as in pickle serialization
        return _WriteHandler(self.index_abspath, 'ab')

    def get_create_handler(self) -> '_WriteHandler':
        """
        Get write file handler.
        :return: write handler.
        """

        self._start = 0  # override _start position
        return _WriteHandler(self.index_abspath, 'wb')

    def get_query_handler(self) -> '_ReadHandler':
        """
        Get read file handler.
        :return: read handler.
        """
        return _ReadHandler(self.index_abspath, self.key_length)

    def _add(
        self, keys: Iterable[str], values: Iterable[bytes], write_handler: _WriteHandler
    ):
        for key, value in zip(keys, values):
            l = len(value)  #: the length
            p = (
                int(self._start / self._page_size) * self._page_size
            )  #: offset of the page
            r = (
                self._start % self._page_size
            )  #: the remainder, i.e. the start position given the offset
            # noinspection PyTypeChecker
            write_handler.header.write(
                np.array(
                    (key, p, r, r + l),
                    dtype=[
                        ('', (np.str_, self.key_length)),
                        ('', np.int64),
                        ('', np.int64),
                        ('', np.int64),
                    ],
                ).tobytes()
            )
            self._start += l
            write_handler.body.write(value)
            self._size += 1

    @requests(on='delete')
    def delete(self, keys: Iterable[str], *args, **kwargs) -> None:
        """Delete the serialized documents from the index via document ids.
        :param keys: a list of ``id``, i.e. ``doc.id`` in protobuf
        :param args: not used
        :param kwargs: not used
        """
        keys = self._filter_nonexistent_keys(keys, self.query_handler.header.keys())
        del self.query_handler
        self.handler_mutex = False
        if keys:
            self._delete(keys)

    def _delete(self, keys: Iterable[str]) -> None:
        with self.write_handler as write_handler:
            for key in keys:
                write_handler.header.write(
                    np.array(
                        tuple(np.concatenate([[key], HEADER_NONE_ENTRY])),
                        dtype=[
                            ('', (np.str_, self.key_length)),
                            ('', np.int64),
                            ('', np.int64),
                            ('', np.int64),
                        ],
                    ).tobytes()
                )
                self._size -= 1

    def _query(self, keys: Iterable[str]) -> List[bytes]:
        query_results = []
        for key in keys:
            pos_info = self.query_handler.header.get(key, None)
            if pos_info is not None:
                p, r, l = pos_info
                with mmap.mmap(self.query_handler.body, offset=p, length=l) as m:
                    query_results.append(m[r:])
            else:
                query_results.append(None)

        return query_results

class FileQueryIndexer(Executor, FileWriterMixin):
    """
    A DBMS Indexer (no query method)
    :param index_filename: the name of the file for storing the index, when not given metas.name is used.
    :param key_length: the default minimum length of the key, will be expanded one time on the first batch
    :param args:  Additional positional arguments which are just used for the parent initialization
    :param kwargs: Additional keyword arguments which are just used for the parent initialization
    """

    def __init__(
        self,
        source_path: str,
        index_filename: Optional[str] = None,
        key_length: int = 36,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.index_filename = index_filename or self.metas.name

        self.key_length = key_length
        self._size = 0

        self._start = 0
        self._page_size = mmap.ALLOCATIONGRANULARITY
        self.logger = JinaLogger(self.__class__.__name__)

        self._load_dump(source_path)
        self.query_handler = self.get_query_handler()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def size(self) -> int:
        """
        The number of vectors or documents indexed.
        :return: size
        """
        return self._size

    def close(self):
        """Close all file-handlers and release all resources. """
        self.logger.info(
            f'indexer size: {self.size} physical size: {get_readable_size(FileQueryIndexer.physical_size(self.workspace))}'
        )
        self.query_handler.close()
        super().close()

    @property
    def index_abspath(self) -> str:
        """
        Get the file path of the index storage
        :return: absolute path
        """
        os.makedirs(self.workspace, exist_ok=True)
        return os.path.join(self.workspace, self.index_filename)

    def _load_dump(self, path):
        """Load the dump at the path
        :param path: the path of the dump"""
        ids, metas = import_metas(path, str(self.metas.pea_id))
        with self.get_create_handler() as write_handler:
            self._add(list(ids), list(metas), write_handler)

    @requests(on='/search')
    def search(
        self, docs: DocumentArray, parameters: Dict = None, *args, **kwargs
    ) -> None:
        """Get a document by its id
        :param keys: the ids
        :param args: not used
        :param kwargs: not used
        :return: List of the bytes of the Documents (or None, if not found)
        """
        if parameters is None:
            parameters = {}

        for docs_array in docs.traverse(parameters.get('traversal_paths', ['r'])):
            self._search(docs_array, parameters.get('is_update', True))

    def _search(self, docs, is_update):
        miss_idx = (
            []
        )  #: missed hit results, some search may not end with results. especially in shards

        serialized_docs = self._query([d.id for d in docs])

        for idx, (retrieved_doc, serialized_doc) in enumerate(
            zip(docs, serialized_docs)
        ):
            if serialized_doc:
                r = Document(serialized_doc)
                if is_update:
                    retrieved_doc.update(r)
                else:
                    retrieved_doc.CopyFrom(r)
            else:
                miss_idx.append(idx)

        # delete non-existed matches in reverse
        for j in reversed(miss_idx):
            del docs[j]

    @staticmethod
    def physical_size(directory: str) -> int:
        """Return the size of the given directory in bytes
        :param directory: directory as :str:
        :return: byte size of the given directory
        """
        root_directory = Path(directory)
        return sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())

class NumpyFileQueryIndexer(Executor):
    def __init__(self, source_path, *args, **kwargs):
        super().__init__(**kwargs)
        #print(f'docs{docs}')
        self._docs = DocumentArray()
        self._vec_indexer = NumpyIndexer(source_path=source_path, *args, **kwargs)
        self._kv_indexer = FileQueryIndexer(source_path=source_path, *args, **kwargs)
        #self._add_metas({'workspace':'./workspace'})

    @requests(on='/index')
    def index(self, docs: 'DocumentArray', parameters: Dict = None, **kwargs):
        '''
        self._vec_indexer.(docs, parameters)
        self._kv_indexer.'''
        self._docs = docs
        print('**************************')
        self._docs.save('./data/toy-output.txt')


    @requests(on='/search')
    def search(self, docs: 'DocumentArray', parameters: Dict = None, **kwargs):
        self._vec_indexer.search(docs, parameters)
        kv_parameters = copy.deepcopy(parameters)

        kv_parameters['traversal_paths'] = [
            path + 'm' for path in kv_parameters.get('traversal_paths', ['r'])
        ]

        self._kv_indexer.search(docs, kv_parameters)

class NumpyIndexer(Executor):
    def __init__(self, source_path: str, **kwargs):
        super().__init__(**kwargs)
        ids, vecs = import_vectors(source_path, str(self.metas.pea_id))
        self._ids = np.array(list(ids))
        self._vecs = np.array(list(vecs))
        self._ids_to_idx = {}

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

    @requests(on='/search')
    def search(self, docs: 'DocumentArray', parameters: Dict = None, **kwargs):
        if parameters is None:
            parameters = {'top_k': 5}
        doc_embeddings = np.stack(docs.get_attributes('embedding'))
        q_emb = _ext_A(_norm(doc_embeddings))
        d_emb = _ext_B(_norm(self._vecs))
        dists = _cosine(q_emb, d_emb)
        positions, dist = self._get_sorted_top_k(dists, int(parameters['top_k']))
        for _q, _positions, _dists in zip(docs, positions, dist):
            for position, _dist in zip(_positions, _dists):
                d = Document(id=self._ids[position], embedding=self._vecs[position])
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