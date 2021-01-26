__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import json
import os

import pytest

from jina.flow import Flow

NUM_DOCS = 3
TOP_K = 3


def config(tmpdir):
    os.environ['JINA_DATA'] = 'tests/test-data/*.png'
    os.environ['JINA_PORT'] = str(45678)
    os.environ['JINA_SHARDS'] = str(1)
    os.environ['JINA_SHARDS_INDEXERS'] = str(1)
    os.environ['JINA_WORKSPACE'] = str(tmpdir)


def index_documents():
    f = Flow().load_config('flows/index.yml')

    with f:
        f.index_files(os.environ['JINA_DATA'], request_size=64, read_mode='rb', size=NUM_DOCS)


def call_api(url, payload=None, headers={'Content-Type': 'application/json'}):
    import requests
    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=TOP_K):
    return call_api(
        'http://0.0.0.0:45678/api/search',
        payload={'top_k': top_k, 'mode': 'search', 'data': [query]})


def get_flow():
    f = Flow().load_config('flows/query.yml')
    f.use_rest_gateway()
    return f


@pytest.fixture
def object_image_paths():
    return ['tests/test-data/1.png', 'tests/test-data/2.png', 'tests/test-data/3.png']


def test_query(tmpdir, object_image_paths):
    config(tmpdir)
    index_documents()
    f = get_flow()
    with f:
        for object_image_path in object_image_paths:
            output = get_results(object_image_path)
            matches = output['search']['docs'][0]['matches']
            assert len(matches) == TOP_K
