__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__copyright__ = 'Copyright (c) 2020 Jina AI Limited. All rights reserved.'
__license__ = 'Apache-2.0'

import json
import os
import sys
import subprocess

from jina.executors import BaseExecutor
from jina.executors.indexers.keyvalue import BinaryPbIndexer
from jina.executors.indexers.vector import NumpyIndexer
from jina.flow import Flow
import pytest

NUM_DOCS = 100
TOP_K = 3
INDEX_FLOW_FILE_PATH = 'flow-index.yml'
QUERY_FLOW_FILE_PATH = 'flow-query.yml'


def config(tmpdir):
    os.environ['JINA_DATA_FILE_1'] = 'tests/data-index-1.csv'
    os.environ['JINA_DATA_FILE_2'] = 'tests/data-index-2.csv'
    os.environ['JINA_WORKSPACE'] = str(tmpdir)
    os.environ['JINA_PORT'] = str(45678)


def assert_index_size(expected_size):
    with BaseExecutor.load(
        os.path.join(os.environ['JINA_WORKSPACE'], 'indexer-0', 'vecidx.bin')
    ) as vector_indexer:
        assert isinstance(vector_indexer, NumpyIndexer)
        assert vector_indexer._size == expected_size

    with BaseExecutor.load(
        os.path.join(os.environ['JINA_WORKSPACE'], 'indexer-0', 'docidx.bin')
    ) as doc_indexer:
        assert isinstance(doc_indexer, BinaryPbIndexer)
        assert doc_indexer._size == expected_size


def index_documents():
    f = Flow().load_config(INDEX_FLOW_FILE_PATH)

    with f:
        f.index_lines(
            filepath=os.environ['JINA_DATA_FILE_1'], batch_size=8, size=NUM_DOCS
        )

    assert_index_size(50)

    # close flow and index new set of docs
    with f:
        f.index_lines(
            filepath=os.environ['JINA_DATA_FILE_2'], batch_size=8, size=NUM_DOCS
        )

    assert_index_size(100)

    # close flow and index same set of docs as in part 2
    with f:
        f.index_lines(
            filepath=os.environ['JINA_DATA_FILE_2'], batch_size=8, size=NUM_DOCS
        )

    assert_index_size(100)


def call_api(url, payload=None, headers={'Content-Type': 'application/json'}):
    import requests

    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=TOP_K):
    return call_api(
        'http://0.0.0.0:45678/api/search',
        payload={'top_k': top_k, 'mode': 'search', 'data': [f'text:{query}']},
    )


def get_flow():
    f = Flow().load_config(QUERY_FLOW_FILE_PATH)
    f.use_rest_gateway()
    return f


@pytest.fixture
def queries():
    return [
        ('Prime Minister', ['The Prime Minister IS here.', 'In Zurich.', 'Presents.']),
        (
            'kick his ass tomorrow',
            [
                'Yeah, we gotta remember to kick his ass tomorrow.',
                'I\'ll give you tree-fiddy.',
                'Yee-yeah.',
            ],
        ),
        (
            'grocery store',
            ['To the grocery store!', 'The Prime Minister IS here.', 'Weak.'],
        ),
    ]


def test_query(tmpdir, queries):
    config(tmpdir)
    index_documents()
    f = get_flow()
    with f:
        for query, exp_result in queries:
            output = get_results(query)
            matches = output['search']['docs'][0]['matches']
            assert len(matches) == TOP_K  # check the number of docs returned
            result = []
            for match in matches:
                result.append(match['text'])
            assert result == exp_result
