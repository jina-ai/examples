import json
import os
import sys
import shutil
import subprocess

from jina.flow import Flow
import pytest


num_docs = 100
top_k = 3
index_flow_file_path = 'flow-index.yml'
query_flow_file_path = 'flow-query.yml'


def config(tmpdir):
    os.environ['JINA_DATA_FILE'] = 'tests/data-index.csv'
    os.environ['JINA_WORKSPACE'] = str(tmpdir)
    os.environ['JINA_PORT'] = str(45678)


@pytest.fixture
def setup_env():
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests', 'jina[http]'])

def index_documents():
    f = Flow().load_config(index_flow_file_path)

    with f:
        f.index_lines(filepath=os.environ['JINA_DATA_FILE'],
                      batch_size=8,
                      size=num_docs)


def call(method, url, payload=None, headers={'Content-Type': 'application/json'}):
    import requests
    return getattr(getattr(requests, method)(url, data=json.dumps(payload), headers=headers), 'json')()


def get_results(query, top_k=top_k):
    return call('post', 
                'http://0.0.0.0:45678/api/search', 
                payload={'top_k': top_k, 'mode': 'search',  'data': [f'text:{query}']})


def get_flow():
    f = Flow().load_config(query_flow_file_path)
    f.use_rest_gateway()
    return f


@pytest.fixture
def queries():
    return [("Don't say anything\n", ["Don't say anything\n", "Check that: I'll watch that game.\n", "I'm trying to talk\n"]),
            ('Sorry\n', ['Sorry\n', 'Hey\n', 'Allб\n']),
            ("Check that: I'll watch that game.\n", ["Check that: I'll watch that game.\n", "I just think it's a fabulous app\n", 'Could you get that\n'])]


def test_query(setup_env, tmpdir, queries):
    config(tmpdir)
    index_documents()
    f = get_flow()
    with f:
        for query, exp_result in queries:
            output = get_results(query)
            matches = output['search']['docs'][0]['matches']
            assert len(matches) == top_k #check the number of docs returned
            result = []
            for match in matches:
                result.append(match['text'])
            assert result == exp_result
