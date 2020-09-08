__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import shutil

import matplotlib.pyplot as plt
import numpy as np
from jina.drivers.helper import array2pb
from jina.flow import Flow
from jina.proto import jina_pb2

try:
    # remove old index
    shutil.rmtree('test-index-file', ignore_errors=False, onerror=None)
except:
    pass

num_docs = 500
vecs = np.random.rand(num_docs, 2)

index_docs = []

for j in range(num_docs):
    d = jina_pb2.Document()
    d.embedding.CopyFrom(array2pb(vecs[j]))
    index_docs.append(d)

query_doc = jina_pb2.Document()
query_doc.embedding.CopyFrom(array2pb(np.zeros(2)))


def plot(req):
    neighbour1 = vecs[[m.id - 1 for m in req.docs[0].matches], :]
    neighbour2 = vecs[[mm.id - 1 for m in req.docs[0].matches for mm in m.matches]]
    neighbour3 = vecs[[mmm.id - 1 for m in req.docs[0].matches for mm in m.matches for mmm in mm.matches]]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(vecs[:, 0], vecs[:, 1], alpha=0.5)
    ax.scatter(neighbour3[:, 0], neighbour3[:, 1], color='yellow', alpha=0.5)
    ax.scatter(neighbour2[:, 0], neighbour2[:, 1], color='cyan', alpha=0.5)
    ax.scatter(neighbour1[:, 0], neighbour1[:, 1], color='green', alpha=0.5)
    ax.scatter(vecs[0][0], vecs[0][1], color='red', alpha=0.5)
    ax.set_aspect('equal', adjustable='box')
    ax.legend(['index', 'adjacency=3', 'adjacency=2', 'adjacency=1', 'query'], title='high order matches')
    plt.show()


f = Flow(callback_on_body=True).add(uses='test-adj.yml')

with f:
    f.index(index_docs)

with f:
    f.search([index_docs[0]], output_fn=plot)
