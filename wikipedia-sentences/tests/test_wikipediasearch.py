__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import itertools as it

import pytest
import json

from jina.flow import Flow
from jina import Document

NUM_DOCS = 100
TOP_K = 3
INDEX_FLOW_FILE_PATH = 'flows/index.yml'
QUERY_FLOW_FILE_PATH = 'flows/query.yml'


def config(tmpdir):
    os.environ['JINA_DATA_FILE'] = 'toy-input.txt'
    os.environ['JINA_WORKSPACE'] = str(tmpdir)
    os.environ['JINA_PORT'] = str(45678)


def index_documents():
    f = Flow().load_config(INDEX_FLOW_FILE_PATH)

    with f:
        data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None))
        f.index_lines(filepath=data_path, batch_size=16, read_mode='r', size=NUM_DOCS)


def call_api(url, payload=None, headers={'Content-Type': 'application/json'}):
    import requests
    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=TOP_K):

    output =  call_api(
        'http://0.0.0.0:45678/api/search',
        payload={"top_k": top_k, "mode": "search", "data": [f"{query}"]}
    )
    return output


def get_flow():
    f = Flow().load_config(QUERY_FLOW_FILE_PATH)
    f.use_rest_gateway()
    return f


@pytest.fixture
def queries():
    output = [
        ("Don't say anything\n",
         [
             'His most recent novel in this series, The Bangkok Asset, was published on 4 August 2015.\n',
             'Their land was taken back by the Spanish Crown; and then irretrievably lost however, when California became part of the United States.\n',
             '"Super Scooter Happy" was covered by Kyary Pamyu Pamyu on her 2013 album, Nanda Collection.\n'
         ]
        )
    ]

    return output


def test_query(tmpdir, queries):
    config(tmpdir)
    index_documents()
    f = get_flow()
    with f:
        for query, exp_result in queries:
            output = get_results(query)
            matches = []
            docs = output['search']['docs'][0]['matches']
            assert len(docs) == TOP_K  # check the number of docs returned
            result = []
            for match in docs:
                result.append(match['text'])

            assert result == exp_result
