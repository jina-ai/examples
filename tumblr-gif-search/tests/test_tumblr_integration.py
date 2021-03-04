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
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45680))


def index_documents():
    f = Flow().load_config('flow-index.yml')

    with f:
        f.index_files(GIF_BLOB, request_size=REQ_SIZE, read_mode='rb')


def get_flow():
    f = Flow().load_config('flow-query.yml')
    f.use_grpc_gateway()
    return f


def validate(req):
    for doc in req.search.docs:
        print(doc)
        assert len(doc.matches) == JINA_TOPK
        for match in doc.matches:
            assert match.uri.startswith('data:image/gif')


def test_query(env_setup):
    index_documents()
    f = get_flow()
    with f:
        f.search_files(glob(GIF_BLOB)[:NR_CASES_SEARCH], on_done=validate)
