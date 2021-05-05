__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import json
import os

import pytest

from jina.flow import Flow

NUM_DOCS = 3
TOP_K = 3

@pytest.fixture
def config(tmpdir):
    import os
    os.system('pip uninstall -y tensorflow-cpu')
    os.system('pip install tensorflow-cpu==2.1')
    os.environ['JINA_DATA'] = 'tests/test-data/*.png'
    os.environ['JINA_PORT'] = str(45680)
    os.environ['JINA_SHARDS'] = str(1)
    os.environ['JINA_SHARDS_INDEXERS'] = str(1)
    os.environ['JINA_WORKSPACE'] = str(tmpdir)

@pytest.fixture
def download_model():
    os.system('./download.sh')


def index_documents():
    f = Flow().load_config('flows/index.yml')

    with f:
        f.index_files(os.environ['JINA_DATA'], request_size=64, read_mode='rb', size=NUM_DOCS)


def call_api(url, payload=None, headers={'Content-Type': 'application/json'}):
    import requests
    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=TOP_K):
    return call_api(
        f'http://0.0.0.0:{os.environ["JINA_PORT"]}/api/search',
        payload={'top_k': top_k, 'mode': 'search', 'data': [query]})


def get_flow():
    f = Flow().load_config('flows/query.yml')
    f.use_grpc_gateway()
    return f


def test_query(config, download_model):
    index_documents()
    f = get_flow()

    def validate(req):
        for doc in req.search.docs:
            for match in doc.matches:
                assert match.uri.startswith('data:image/png;charset=utf-8,')

    from glob import iglob
    with f:
        f.search_files(iglob(os.environ.get('JINA_DATA')), on_done=validate)
