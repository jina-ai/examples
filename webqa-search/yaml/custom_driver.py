
import numpy as np
from jina.drivers import BaseExecutableDriver
from jina.drivers.helper import extract_chunks
import json

class TitleIndexDriver(BaseExecutableDriver):
    """Extract title-level embeddings and add it to the executor

    """

    def __call__(self, *args, **kwargs):
        embed_vecs, chunk_pts, no_chunk_docs, bad_chunk_ids = extract_chunks(self.req.docs, embedding=True)

        if no_chunk_docs:
            self.pea.logger.warning('these docs contain no chunk: %s' % no_chunk_docs)

        if bad_chunk_ids:
            self.pea.logger.warning('these bad chunks can not be added: %s' % bad_chunk_ids)

        if chunk_pts:
            self.exec_fn(np.array([c.doc_id for c in chunk_pts]), np.stack(embed_vecs))

class AnswerIndexDriver(BaseExecutableDriver):

    def __call__(self, *args, **kwargs):
        for d in self.req.docs:
            self.exec_fn(d)
