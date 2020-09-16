__version__ = '0.0.1'

import os
import sys
import h5py
import numpy as np

from jina.flow import Flow
from jina.proto.jina_pb2 import Document
from jina.drivers.helper import array2pb

num_docs = int(os.environ.get('MAX_DOCS', 10))


def uint8_to_float32(x):
    return (np.float32(x) - 128.) / 128.


def bool_to_float32(y):
    return np.float32(y)


def load_hdf5_data(data_fn, size=num_docs):
    with h5py.File(data_fn, 'r') as hf:
        x = hf.get('x')
        # y = hf.get('y')
        video_id_list = hf.get('video_id_list')
        x = np.array(x)
        x = uint8_to_float32(x)
        # y = list(y)
        video_id_list = list(video_id_list)
    for idx, (_emb, _vid) in \
            enumerate(zip(x[:size], video_id_list[:size])):
        doc = Document()
        doc.blob.CopyFrom(array2pb(_emb))
        doc.embedding.CopyFrom(array2pb(np.mean(_emb, axis=0)))
        doc.uri = os.path.join('data', 'wav', f'{_vid.decode()}')
        doc.id = idx + 1
        yield doc


def config():
    parallel = 1 if sys.argv[1] == 'index' else 1
    shards = 2
    os.environ['PARALLEL'] = str(parallel)
    os.environ['SHARDS'] = str(shards)
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))


# for index
def index():

    f = Flow.load_config('flows/index.yml')

    with f:
        f.index(load_hdf5_data('data/packed_features/eval.h5'), batch_size=2, output_fn=print)


# for search
def search():
    f = Flow.load_config('flows/query.yml')

    with f:
        f.search_files('data/test/R9_ZSCveAHg_7s.wav', top_k=5, output_fn=print)
        # f.block()


# for test before put into docker
def dryrun():
    f = Flow.load_config('flows/query.yml')

    with f:
        pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('choose between "index/search/dryrun" mode')
        exit(1)
    if sys.argv[1] == 'index':
        config()
        index()
    elif sys.argv[1] == 'search':
        config()
        search()
    elif sys.argv[1] == 'dryrun':
        config()
        dryrun()
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
