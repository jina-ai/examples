import base64
import io
import json
import os
import sys
import shutil
import subprocess

import pytest

from jina.flow import Flow


num_docs = 3
top_k = 3
index_flow_file_path = 'flow-index.yml'
query_flow_file_path = 'flow-query-original.yml'


def config(tmpdir):
    os.environ['JINA_DATA'] = 'tests/test-data/*.jpg'
    os.environ['JINA_PORT'] = str(45678)
    os.environ['PARALLEL'] = str(1)
    os.environ['SHARDS'] = str(1)
    os.environ['WORKDIR'] = str(tmpdir)


@pytest.fixture
def setup_env():
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..' ))
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests', 'jina[http]'])


def index_documents():
    f = Flow().load_config(index_flow_file_path)

    with f:
        f.index_files(os.environ['JINA_DATA'], batch_size=1, read_mode='rb', size=num_docs)


def image_to_byte_array(image, format):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=format)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def read_and_convert2png(file_path):
    from PIL import Image
    im = Image.open(file_path)
    png_bytes = image_to_byte_array(im, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(png_bytes).decode()


def call(method, url, payload=None, headers={'Content-Type': 'application/json'}):
    import requests
    return getattr(getattr(requests, method)(url, data=json.dumps(payload), headers=headers), 'json')()


def get_results(query, top_k=top_k):
    return call('post',
                'http://0.0.0.0:45678/api/search', 
                payload={'top_k': top_k, 'mode': 'search',  'data': [query]})


def get_flow():
    f = Flow().load_config(query_flow_file_path)
    f.use_rest_gateway()
    return f


def buffer2png(buffer):
    from PIL import Image
    im = Image.open(io.BytesIO(base64.b64decode(buffer)))
    png_bytes = image_to_byte_array(im, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(png_bytes).decode()


@pytest.fixture
def queries():
    return [read_and_convert2png('tests/test-data/dog.jpg'), 
            read_and_convert2png('tests/test-data/horse.jpg'),
            read_and_convert2png('tests/test-data/jacket.jpg')]


def test_query(setup_env, tmpdir, queries):
    config(tmpdir)
    index_documents()
    f = get_flow()
    with f:
        for query in queries:
            output = get_results(query)
            matches = output['search']['docs'][0]['matches']
            buffer = matches[0]['buffer'] #getting buffer of first match
            assert query == buffer2png(buffer) #first match should be the query itself
