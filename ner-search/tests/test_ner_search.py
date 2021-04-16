__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import itertools as it

import pytest
import json

from jina.flow import Flow
from jina import Document

import sys

sys.path.append('..')
from ner_ranker import *


NUM_DOCS = 100
TOP_K = 3
INDEX_FLOW_FILE_PATH = 'flows/index.yml'
QUERY_NER_FLOW_FILE_PATH = 'flows/query_ner.yml'
QUERY_BASCIC_FLOW_FILE_PATH = 'flows/query_basic.yml'


def config(tmpdir):
    os.environ['JINA_DATA_FILE'] = os.path.join('..', 'data', 'toy-input.txt')
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


def get_results(query, flow, top_k=TOP_K):
    output = call_api(
        f'http://0.0.0.0:{flow.port_expose}/search', payload={"top_k": top_k, "mode": "search", "data": [f"{query}"]}
    )
    return output


def get_flow(file):
    f = Flow().load_config(file)
    f.use_rest_gateway()
    return f


def test_query(tmpdir):
    config(tmpdir)
    index_documents()
    ner_results = []
    with get_flow(QUERY_NER_FLOW_FILE_PATH) as ner_query:
        output = get_results('restaurants in San Francisco\n', ner_query)
        docs = output['search']['docs'][0]['matches']
        assert len(docs) == TOP_K  # check the number of docs returned
        for match in docs:
            ner_results.append((match['text'], match['score']['value']))

    basic_results = []
    with get_flow(QUERY_BASCIC_FLOW_FILE_PATH) as ner_query:
        output = get_results('restaurants in San Francisco\n', ner_query)
        docs = output['search']['docs'][0]['matches']
        assert len(docs) == TOP_K  # check the number of docs returned
        for match in docs:
            basic_results.append((match['text'], match['score']['value']))

    print('### NER results:')
    print(f'### {ner_results}')
    assert [m[0] for m in ner_results] == [
        'San Francisco cheap food\n',  # more important because matches both value and type of entity
        'Los Angeles cuisine\n',  # more imp. because it matches entity type
        'take-away in my city\n',
    ]
    print('basic results:')
    print(f'### {basic_results}')
    assert [m[0] for m in basic_results] == [
        'take-away in my city\n',
        'San Francisco cheap food\n',
        'Los Angeles cuisine\n',
    ]
