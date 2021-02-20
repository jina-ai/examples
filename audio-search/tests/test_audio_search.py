__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import json
import os
from sys import platform

import pytest
import requests
from jina.flow import Flow

JINA_TOPK = 2
NUM_DOCS = 3


@pytest.fixture()
def env_setup(tmpdir):
    os.environ['JINA_SHARDS'] = str(2)
    os.environ['JINA_WORKSPACE'] = str(tmpdir)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))
    os.environ['JINA_TOPK'] = str(JINA_TOPK)
    if platform == "linux":
        os.system('sudo apt-get install libsndfile1')


@pytest.fixture
def download_model():
    os.system('./download_model.sh')


def index_documents():
    f = Flow().load_config('flows/index.yml')
    with f:
        f.index_files('tests/data/*.wav', batch_size=2, size=NUM_DOCS)


def call_api(url, payload=None):
    headers = {'Content-Type': 'application/json'}
    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=JINA_TOPK):
    return call_api(
        f'http://0.0.0.0:{os.environ["JINA_PORT"]}/api/search',
        payload={'top_k': top_k, 'mode': 'search', 'data': [query]})


def get_flow():
    f = Flow().load_config('flows/query.yml')
    f.use_rest_gateway()
    return f


@pytest.fixture()
def queries():
    return ['Y-0BIyqJj9ZU', 'Y-0CamVQdP_Y', 'Y-0Gj8-vB1q4']


def test_query(env_setup, download_model, queries):
    index_documents()
    f = get_flow()
    paths = queries
    with f:
        for path in paths:
            object_path = 'tests/data/' + path + '.wav'
            output = get_results(object_path)
            matches = output['search']['docs'][0]['matches']
            assert len(matches) >= 1
