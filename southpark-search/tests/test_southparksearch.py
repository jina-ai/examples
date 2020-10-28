__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import json
import os
import sys
import subprocess

from jina.flow import Flow
import pytest


NUM_DOCS = 100
TOP_K = 3
INDEX_FLOW_FILE_PATH = 'flow-index.yml'
QUERY_FLOW_FILE_PATH = 'flow-query.yml'


def config(tmpdir):
    os.environ['JINA_DATA_FILE'] = 'tests/data-index.csv'
    os.environ['JINA_WORKSPACE'] = str(tmpdir)
    os.environ['JINA_PORT'] = str(45678)


def index_documents():
    f = Flow().load_config(INDEX_FLOW_FILE_PATH)

    with f:
        f.index_lines(filepath=os.environ['JINA_DATA_FILE'],
                      batch_size=8,
                      size=NUM_DOCS)


def call_api(url, payload=None, headers={'Content-Type': 'application/json'}):
    import requests
    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=TOP_K):
    return call_api(
        'http://0.0.0.0:45678/api/search',
        payload={"top_k": top_k, "mode": "search", "data": [f"text:{query}"]}
    )


def get_flow():
    f = Flow().load_config(QUERY_FLOW_FILE_PATH)
    f.use_rest_gateway()
    return f


@pytest.fixture
def queries():
    return [("Don't say anything\n", ["Don't say anything\n", "Check that: I'll watch that game.\n", "I'm trying to talk\n"]),
            ('Sorry\n', ['Sorry\n', 'Hey\n', 'Allб\n']),
            ("Check that: I'll watch that game.\n", ["Check that: I'll watch that game.\n", "I just think it's a fabulous app\n", 'Could you get that\n'])]


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
