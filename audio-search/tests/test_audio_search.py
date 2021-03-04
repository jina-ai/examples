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
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65480))
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


def get_flow():
    f = Flow().load_config('flows/query.yml')
    f.use_grpc_gateway()
    return f


def test_query(env_setup, download_model):
    index_documents()
    f = get_flow()
    fn_list = ['Y-0BIyqJj9ZU', 'Y-0CamVQdP_Y', 'Y-0Gj8-vB1q4']
    test_filepath_list = [f'tests/data/{_fn}.wav' for _fn in fn_list]

    def validate(req):
        for doc in req.search.docs:
            assert doc.matches[0].uri.startswith('data:audio/x-wav')

    with f:
        f.search_files(test_filepath_list, on_done=validate)
