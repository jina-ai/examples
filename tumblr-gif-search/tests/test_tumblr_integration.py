__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import json
import os
from glob import glob

import pytest
import requests
from jina.flow import Flow

SHARDS_DOC = 2
SHARDS_CHUNK_SEG = 2
SHARDS_INDEXER = 2
JINA_TOPK = 2
GIF_BLOB = 'tests/data/*.gif'
NR_CASES_SEARCH = 3
REQ_SIZE = 1


@pytest.fixture()
def env_setup(tmpdir):
    os.environ['SHARDS_DOC'] = str(SHARDS_DOC)
    os.environ['JINA_TOPK'] = str(JINA_TOPK)
    os.environ['SHARDS_CHUNK_SEG'] = str(SHARDS_CHUNK_SEG)
    os.environ['SHARDS_INDEXER'] = str(SHARDS_INDEXER)
    os.environ['JINA_WORKSPACE'] = './workspace'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def index_documents():
    f = Flow().load_config('flow-index.yml')

    with f:
        f.index_files(GIF_BLOB, request_size=REQ_SIZE, read_mode='rb', skip_dry_run=True)


def call_api(url, payload=None):
    headers = {'Content-Type': 'application/json'}
    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=JINA_TOPK):
    return call_api(
        f'http://0.0.0.0:{os.environ["JINA_PORT"]}/api/search',
        payload={'top_k': top_k, 'mode': 'search', 'data': [query]})


def get_flow():
    f = Flow().load_config('flow-query.yml')
    f.use_rest_gateway()
    return f


def test_query(env_setup):
    index_documents()
    f = get_flow()
    with f:
        for object_image_path in glob(GIF_BLOB)[:NR_CASES_SEARCH]:
            output = get_results(object_image_path)
            matches = output['search']['docs'][0]['matches']
            assert len(matches) == JINA_TOPK
            for match in matches:
                assert match['uri'].startswith('data:image/gif')
