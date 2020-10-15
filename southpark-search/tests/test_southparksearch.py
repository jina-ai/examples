import pytest

import json
import os
import sys
import shutil
import subprocess
from typing import List

from jina.flow import Flow


os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..' ))


num_docs = 100 
top_k = 3
index_flow_file_path = "flow-index.yml"
query_flow_file_path = "flow-query.yml"


def config():
	os.environ["JINA_DATA_FILE"] = os.environ.get("JINA_DATA_FILE", "tests/data-index.csv")
	os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")
	os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))


def prepare_data():
    pass


def setup_env():
	subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
	subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "jina[http]"])


def index_documents():
    f = Flow().load_config(index_flow_file_path)

    with f:
        f.index_lines(
            filepath=os.environ["JINA_DATA_FILE"],
            batch_size=8,
            size=num_docs,
        )


def call(method, url, payload=None, headers={'Content-Type': 'application/json'}):
	import requests
	return getattr(getattr(requests, method)(url, data=json.dumps(payload), headers=headers), 'json')()


def get_results(query, top_k=top_k):
    return call('post', 
    	        'http://0.0.0.0:45678/api/search', 
    	        payload={"top_k": top_k, "mode": "search",  "data": [f"text:{query}"]}
    	        )


def set_flow():
	f = Flow().load_config(query_flow_file_path)
	f.use_rest_gateway()
	return f


@pytest.fixture
def queries():
	return [('hey dude', ["Don't say anything\n", "Check that: I'll watch that game.\n", "Because you're a fucking fatass\n"]),
	        ('sister', ['Sorry\n', 'Lame.\n', 'Christ\n']),
	        ("Ill watch that game", ["Check that: I'll watch that game.\n", 'Quit it\n', 'Sorry\n'])]


def test_query(queries):
	config()
	setup_env()
	prepare_data()
	index_documents()
	f = set_flow()
	with f:
		for query, exp_result in queries:
			output = get_results(query)
			matches = output['search']['docs'][0]['matches']
			assert len(matches) == top_k #check the number of docs returned
			result = []
			for match in matches:
				result.append(match['text'])
			assert result == exp_result


def test_cleanup():
	shutil.rmtree(os.environ['JINA_WORKSPACE'])
