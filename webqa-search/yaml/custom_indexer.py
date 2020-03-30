import gzip
import json
from typing import Union, List

from google.protobuf.json_format import Parse

from jina.drivers.helper import blob2array
from jina.executors.indexers import BaseIndexer
from jina.proto import jina_pb2
import numpy as np


class AnswerIndexer(BaseIndexer):
    def __init__(self, metric: str = 'euclidean', compress_level: int = 1, title_weight: float = 0.8,
                 answer_weight: float=0.2, *args, **kwargs):
        """

        :param metric: The distance metric to use. `braycurtis`, `canberra`, `chebyshev`, `cityblock`, `correlation`,
                        `cosine`, `dice`, `euclidean`, `hamming`, `jaccard`, `jensenshannon`, `kulsinski`,
                        `mahalanobis`,
                        `matching`, `minkowski`, `rogerstanimoto`, `russellrao`, `seuclidean`, `sokalmichener`,
                        `sokalsneath`, `sqeuclidean`, `wminkowski`, `yule`.
        :param compress_level: The compresslevel argument is an integer from 0 to 9 controlling the
                        level of compression; 1 is fastest and produces the least compression,
                        and 9 is slowest and produces the most compression. 0 is no compression
                        at all. The default is 9.

        :param title_weight: the weight of title, used by calculate total distance
        :param answer_weight: the weight of answer, used by calculate total distance
        """
        super().__init__(*args, **kwargs)
        self.metric = metric
        self.compress_level = compress_level

        if title_weight + answer_weight != 1:
            raise ValueError('the sum of title weight and answer weight must must be 1')
        self.title_weight = title_weight
        self.answer_weight = answer_weight

    def get_create_handler(self):
        """Creat a new gzip file"""
        return self.get_add_handler()

    def get_add_handler(self):
        """Append to the existing gzip file using text appending mode """

        # note this write mode must be append, otherwise the index will be overwrite in the search time
        return gzip.open(self.index_abspath, 'at', compresslevel=self.compress_level)

    def add(self, obj):
        """Add a JSON-friendly object to the indexer

        :param obj: an object can be jsonify
        """

        json.dump(obj, self.write_handler)
        self.write_handler.write('\n')

    def get_query_handler(self):
        """get query handler"""
        r = {}
        self._answers = {}
        with gzip.open(self.index_abspath, 'rt') as fp:
            for l in fp:
                if l:
                    tmp = json.loads(l)
                    for k, v in tmp.items():
                        chunks = Parse(v, jina_pb2.Document()).chunks
                        qid = chunks[0].doc_id
                        r[qid] = {}
                        for c in chunks:
                            r[qid][c.chunk_id] = blob2array(c.embedding)
                            self._answers[c.chunk_id] = c.text

        return r

    def query(self, keys: np.array, title_topk: tuple, topk: int, *args, **kwargs) -> Union[List[str], np.array, np.array]:
        """ Find the top k answer chunks

        :param keys: title id and title distance
        :param title_topk: title id and title distance
        :param topk: how many top answer return
        :return: protobuf chunk of answer
        """
        from scipy.spatial.distance import cdist

        vecs = []
        answer_ids = []
        title_dists = []
        dists = []
        for qid, score in title_topk:
            for answer_id, vec in self.query_handler[qid].items():
                vecs.append(vec)
                answer_ids.append(answer_id)
                title_dists.append(score)

        vecs = np.array(vecs)
        dist = cdist(keys, vecs, metric=self.metric)
        for title_score, answer_score in zip(title_dists, dist[0]):
            dists.append(title_score * self.title_weight + answer_score * self.answer_weight)

        dists = np.array(dists)
        tmp = np.array(dists).argsort()[:topk]
        topk_answer_ids = np.array(answer_ids)[tmp]
        texts = [self._answers[answer_id] for answer_id in topk_answer_ids]

        return texts, topk_answer_ids, dists[tmp]
