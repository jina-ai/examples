__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import gzip
import os
import urllib.request

import numpy as np
from jina import Document
from jina.executors.encoders import BaseImageEncoder
from jina.flow import Flow
from jina.logging.profile import ProgressBar
from pkg_resources import resource_filename


class MyEncoder(BaseImageEncoder):
    """Simple Encoder used in :command:`jina hello-world`,
        it transforms the original 784-dim vector into a 64-dim vector using
        a random orthogonal matrix, which is stored and shared in index and query time"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # generate a random orthogonal matrix
        H = np.random.rand(784, 64)
        u, s, vh = np.linalg.svd(H, full_matrices=False)
        self.oth_mat = u @ vh
        self.touch()

    def encode(self, data: 'np.ndarray', *args, **kwargs):
        # reduce dimension to 50 by random orthogonal projection
        return (data.reshape([-1, 784]) / 255) @ self.oth_mat


TOP_K = 10
NUM_DOCS_QUERY = 100
NUM_DOCS_INDEX = 600

label_id = {
    0: 'T-shirt/top',
    1: 'Trouser',
    2: 'Pullover'
}


def get_mapped_label(label_int: str):
    """
    Get a label_int and return the description of that label
    label_int	Description
    0	        T-shirt/top
    1	        Trouser
    2	        Pullover
    """
    return label_id.get(label_int, "Invalid tag")


def load_mnist(path: str):
    with gzip.open(path, 'rb') as fp:
        return np.frombuffer(fp.read(), dtype=np.uint8, offset=16).reshape([-1, 784])


def load_labels(path: str):
    with gzip.open(path, 'rb') as fp:
        return np.frombuffer(fp.read(), dtype=np.uint8, offset=8).reshape([-1, 1])


def download_data(target: dict, download_proxy=None):
    opener = urllib.request.build_opener()
    if download_proxy:
        proxy = urllib.request.ProxyHandler({'http': download_proxy, 'https': download_proxy})
        opener.add_handler(proxy)
    urllib.request.install_opener(opener)
    with ProgressBar(task_name='download fashion-mnist', batch_unit='') as t:
        for k, v in target.items():
            if not os.path.exists(v['filename']):
                urllib.request.urlretrieve(v['url'], v['filename'], reporthook=lambda *x: t.update(1))
            if k == 'index-labels' or k == 'query-labels':
                v['data'] = load_labels(v['filename'])
            if k == 'index' or k == 'query':
                v['data'] = load_mnist(v['filename'])


def index_generator(num_doc: int, target: dict):
    for j in range(num_doc):
        label_int = target['index-labels']['data'][j][0]
        if label_int < 3:  # We are using only 3 categories, no need to index the rest
            with Document() as d:
                d.content = target['index']['data'][j]
                category = get_mapped_label(label_int)
                d.tags['label'] = category
            yield d


def query_generator(num_doc: int, target: dict):
    for j in range(num_doc):
        label_int = target['query-labels']['data'][j][0]
        category = get_mapped_label(label_int)

        if category == 'Pullover':
            d = Document(content=(target['query']['data'][j]))
            d.tags['label'] = category
            yield d


def config():
    shards_encoder = 1
    shards_indexer = 1
    os.environ['JINA_RESOURCE_DIR'] = resource_filename('jina', 'resources')
    os.environ['JINA_SHARDS_INDEXER'] = str(shards_indexer)
    os.environ['JINA_SHARDS_ENCODER'] = str(shards_encoder)
    os.environ['JINA_WORKDIR'] = './workspace'
    os.makedirs(os.environ['JINA_WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45683))


def test_query(mocker):
    def extract_result(resp):
        result = []
        num_of_queries = []
        for data in resp.search.docs:
            num_of_queries.append(data)
            for match in data.matches:
                match_label = match.tags['label']
                result.append(match_label)
        return result, num_of_queries

    def search_done(resp):
        result, num_of_queries = extract_result(resp)
        validate(result, num_of_queries)

    m = mocker.Mock()

    def validate(result, num_of_queries):
        m()
        result_set = set(result)
        contain_query = 'Pullover' in result_set

        assert len(result) == TOP_K * len(num_of_queries)  # Make sure we query correct amount of data
        assert contain_query and len(result_set) == 1  # Make sure we query correct data 'Pullover'

    targets = {
        'index-labels': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-labels-idx1-ubyte.gz',
            'filename': os.path.join('./workspace', 'index-labels')
        },
        'query-labels': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-labels-idx1-ubyte.gz',
            'filename': os.path.join('./workspace', 'query-labels')
        },
        'index': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-images-idx3-ubyte.gz',
            'filename': os.path.join('./workspace', 'index')
        },
        'query': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-images-idx3-ubyte.gz',
            'filename': os.path.join('./workspace', 'query')
        }
    }

    config()
    download_data(targets, None)

    f = Flow.load_config('flows/index.yml')

    with f:
        f.index(index_generator(NUM_DOCS_INDEX, targets), request_size=2048)

    f = Flow.load_config('flows/query.yml')

    with f:
        f.search(query_generator(NUM_DOCS_QUERY, targets), shuffle=False, size=128,
                 on_done=search_done, request_size=32, top_k=TOP_K)

    m.assert_called()
