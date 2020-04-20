from jina.executors.crafters import BaseDocCrafter
from jina.executors.rankers.tfidf import TfIdfRanker
import json
import numpy as np


class DictEntryExtractor(BaseDocCrafter):
    def craft(self, doc_id, raw_bytes, *args, **kwargs):
        json_str = raw_bytes.decode('utf8')
        json_dict = json.loads(json_str)
        word = json_dict['word'].lower()
        def_text = json_dict['text'].lower()
        weight = json_dict['weight']
        doc_dict = {
            'raw_bytes': f'{word}: {def_text}'.encode('utf8'),
            'doc_id': doc_id,
            'weight': weight,
            'meta_info': raw_bytes
        }
        return doc_dict


class MaxRanker(TfIdfRanker):
    def score(self, match_idx, query_chunk_meta, match_chunk_meta):
        _sorted_m = match_idx[match_idx[:, self.col_doc_id].argsort()]
        _, _doc_counts = np.unique(_sorted_m[:, self.col_doc_id], return_counts=True)
        _group_by_doc_id = np.split(_sorted_m, np.cumsum(_doc_counts))
        r = []
        for _g in _group_by_doc_id:
            if _g.shape[0] == 0:
                continue
            _q_tf = self.get_tf(_g, match_chunk_meta)
            _q_id = _g[0, 0]
            _q_score = self._get_score(_g)
            r.append((_q_id, _q_score))
        r = np.array(r, dtype=np.float64)
        r = r[r[:, -1].argsort()[::-1]]
        return r

