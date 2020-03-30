
from jina.drivers import BaseExecutableDriver
from jina.drivers.helper import extract_chunks
from jina.drivers.helper import blob2array
import numpy as np

class AnswerSearchDriver(BaseExecutableDriver):
    """Fill in the chunk-level top-k results using the AnswerIndexer

    """

    def __call__(self, *args, **kwargs):
        for d in self.req.docs:
            chunk = d.chunks[0] # when query, every document just has one chunk
            title_topk = [(c.match_doc.doc_id, c.score.value) for c in chunk.topk_results]
            texts, topk_answer_ids, topk_dists = self.exec_fn(np.array([blob2array(chunk.embedding)]), title_topk,
                                                               self.req.top_k)

            for c, text, answer_id, dist in zip(chunk.topk_results, texts, topk_answer_ids, topk_dists):
                c.match_chunk.text = text
                c.match_chunk.chunk_id = answer_id
                c.score.value = dist

class TitleSearchDriver(BaseExecutableDriver):
    """Extract chunk-level embeddings from the request and use the executor to query it

    """

    def __call__(self, *args, **kwargs):
        embed_vecs, chunk_pts, no_chunk_docs, bad_chunk_ids = extract_chunks(self.req.docs, embedding=True)

        if no_chunk_docs:
            self.logger.warning('these docs contain no chunk: %s' % no_chunk_docs)

        if bad_chunk_ids:
            self.logger.warning('these bad chunks can not be added: %s' % bad_chunk_ids)

        idx, dist = self.exec_fn(embed_vecs, top_k=self.req.top_k)
        op_name = self.exec.__class__.__name__
        for c, topks, scs in zip(chunk_pts, idx, dist):
            for m, s in zip(topks, scs):
                r = c.topk_results.add()
                r.match_doc.doc_id = m
                r.score.value = s
                r.score.op_name = op_name

class TitleIndexDriver(BaseExecutableDriver):
    """Extract chunk-level embeddings and add it to the executor

    """

    def __call__(self, *args, **kwargs):
        embed_vecs, chunk_pts, no_chunk_docs, bad_chunk_ids = extract_chunks(self.req.docs, embedding=True)

        if no_chunk_docs:
            self.pea.logger.warning('these docs contain no chunk: %s' % no_chunk_docs)

        if bad_chunk_ids:
            self.pea.logger.warning('these bad chunks can not be added: %s' % bad_chunk_ids)

        if chunk_pts:
            self.exec_fn(np.array([c.doc_id for c in chunk_pts]), np.stack(embed_vecs))

