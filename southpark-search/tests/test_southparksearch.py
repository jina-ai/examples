__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import pytest

import json
import os
import sys
import subprocess

from jina.flow import Flow

NUM_DOCS = 100
TOP_K = 3
INDEX_FLOW_FILE_PATH = "flow-index.yml"
QUERY_FLOW_FILE_PATH = "flow-query.yml"


def config(tmpdir):
    os.environ["JINA_DATA_FILE"] = os.environ.get("JINA_DATA_FILE", "tests/data-index.csv")
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", str(tmpdir))
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))


def setup_env():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "jina[http]"])


def index_documents():
    f = Flow().load_config(INDEX_FLOW_FILE_PATH)

    with f:
        f.index_lines(filepath=os.environ["JINA_DATA_FILE"],
                      batch_size=8,
                      size=NUM_DOCS)


def call_api(url, payload=None, headers={'Content-Type': 'application/json'}):
    import requests
    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=TOP_K):
    return call_api(
        'http://0.0.0.0:45678/api/search',
        payload={"top_k": TOP_K, "mode": "search", "data": [f"text:{query}"]}
    )


def set_flow():
    f = Flow().load_config(QUERY_FLOW_FILE_PATH)
    f.use_rest_gateway()
    return f


@pytest.fixture
def queries():
    return [('hey dude',
             ["Don't say anything\n", "Check that: I'll watch that game.\n", "Because you're a fucking fatass\n"]),
            ('sister', ['Sorry\n', 'Lame.\n', 'Christ\n']),
            ("Ill watch that game", ["Check that: I'll watch that game.\n", 'Quit it\n', 'Sorry\n'])]


def test_query(queries, tmpdir):
    config(tmpdir)
    setup_env()
    index_documents()
    f = set_flow()
    with f:
        for query, exp_result in queries:
            output = get_results(query)
            matches = output['search']['docs'][0]['matches']
            assert len(matches) == TOP_K  # check the number of docs returned
            result = []
            for match in matches:
                result.append(match['text'])
            assert result == exp_result
