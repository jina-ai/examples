from jina import Flow, DocumentArray, Document
from executors import AggregateRanker
import numpy as np

def test_aggregate(tmpdir):
     metas = {'workspace': str(tmpdir)}
     f = (Flow()
             .add(uses='jinahub://SimpleIndexer',
                  uses_with={'index_file_name': 'name', 'default_traversal_paths': ['c']},
                  uses_meta=metas)
             .add(uses=AggregateRanker, uses_with={'default_traversal_paths': ['c']}))

     doc1 = Document(id='doc1')
     doc1.chunks.append(Document(id='doc1-chunk1'), embedding=np.array([1, 0, 0, 0]))
     doc1.chunks.append(Document(id='doc1-chunk2'), embedding=np.array([0, 1, 0, 0]))

     doc2 = Document(id='doc2')
     doc2.chunks.append(Document(id='doc2-chunk1'), embedding=np.array([0, 0, 1, 0]))
     doc2.chunks.append(Document(id='doc2-chunk2'), embedding=np.array([0, 0, 0, 1]))

     with f:
         f.index(inputs=DocumentArray([doc1, doc2]))
         res = f.search(inputs=DocumentArray([doc1, doc2]), return_results=True)
         q1, q2 = res[0].data.docs
         assert q1.matches[0].id == 'doc1'
         assert q2.matches[0].id == 'doc2'
