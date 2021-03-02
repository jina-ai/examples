__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import base64
import io
import json
import os

import pytest

from jina.flow import Flow


NUM_DOCS = 3
TOP_K = 3
INDEX_FLOW_FILE_PATH = 'flow-index.yml'
QUERY_FLOW_FILE_PATH = 'flow-query-object.yml'


def config(tmpdir):
    os.environ['JINA_DATA'] = 'tests/test-data/*.jpg'
    os.environ['JINA_PORT'] = str(45680)
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
        f'http://0.0.0.0:{os.getenv("JINA_PORT")}/api/search',
        payload={'top_k': top_k, 'mode': 'search',  'data': [query]})


def get_flow():
    f = Flow().load_config(QUERY_FLOW_FILE_PATH)
    return f


@pytest.fixture
def object_image_paths():
    return ['tests/test-data/dog-object.png', ] # 'tests/test-data/horse-object.png', 'tests/test-data/jacket-object.png']


def test_query(tmpdir, object_image_paths):
    config(tmpdir)
    index_documents()
    f = get_flow()

    test_fn_list = ['tests/test-data/dog-object.png', 'tests/test-data/horse-object.png', 'tests/test-data/jacket-object.png']

    def validate(req):
        for doc, fn in zip(req.search.docs, test_fn_list):
            assert doc.matches[0].uri == read_and_convert2png(fn)

    with f:
        f.search_files(test_fn_list, on_done=validate)
