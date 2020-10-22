import base64
import io
import json
import os
import sys
import shutil
import subprocess

import pytest

from jina.flow import Flow


NUM_DOCS = 3
TOP_K = 3
INDEX_FLOW_FILE_PATH = 'flow-index.yml'
QUERY_FLOW_FILE_PATH = 'flow-query-object.yml'


def config(tmpdir):
    os.environ['JINA_DATA'] = 'tests/test-data/*.jpg'
    os.environ['JINA_PORT'] = str(45678)
    os.environ['PARALLEL'] = str(1)
    os.environ['SHARDS'] = str(1)
    os.environ['WORKDIR'] = str(tmpdir)


def index_documents():
    f = Flow().load_config(INDEX_FLOW_FILE_PATH)

    with f:
        f.index_files(os.environ['JINA_DATA'], batch_size=1, read_mode='rb', size=NUM_DOCS)


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


def call_api(url, payload=None, headers={'Content-Type': 'application/json'}):
    import requests
    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=TOP_K):
    return call_api(
        'http://0.0.0.0:45678/api/search', 
         payload={'top_k': top_k, 'mode': 'search',  'data': [query]})


def get_flow():
    f = Flow().load_config(QUERY_FLOW_FILE_PATH)
    f.use_rest_gateway()
    return f


@pytest.fixture
def image_paths():
    return zip(['tests/test-data/dog.jpg', 'tests/test-data/horse.jpg', 'tests/test-data/jacket.jpg'], 
               ['tests/test-data/dog-object.png', 'tests/test-data/horse-object.png', 'tests/test-data/jacket-object.png'])

def test_query(tmpdir, image_paths):
    config(tmpdir)
    index_documents()
    f = get_flow()
    with f:
        for query_image_path, object_image_path in image_paths:
            query_image = read_and_convert2png(query_image_path)
            object_image = read_and_convert2png(object_image_path)
            output = get_results(query_image)
            matches = output['search']['docs'][0]['matches']
            uri = matches[0]['uri'] #getting uri of first match
            assert object_image == uri #first match should be the object image itself
