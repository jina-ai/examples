__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os

import pytest
from jina import Document
from jina import Flow


@pytest.fixture()
def config():
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '4')
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45670))


def index_generator(data_path):
    for path in data_path:
        with Document() as doc:
            doc.content = path
            doc.mime_type = 'application/pdf'
        yield doc


def search_generator(data_path):
    d = Document()
    d.content = data_path
    yield d


def index_documents():
    f = Flow().load_config('flows/index.yml')
    with f:
        pdf_files = ['toy_data/blog1.pdf', 'toy_data/blog2.pdf', 'toy_data/blog3.pdf']
        f.index(input_fn=index_generator(data_path=pdf_files), read_mode='r', request_size=1)


def get_flow():
    f = Flow().load_config('flows/query-multimodal.yml')
    f.use_grpc_gateway()
    return f


def validate(resp):
    for doc in resp.search.docs:
        assert len(doc.matches) == 3
        for match in doc.matches:
            assert match.mime_type == 'application/pdf'


def test_query(config):
    index_documents()
    f = get_flow()
    with f:
        d = Document()
        d.text = 'It makes sense to first define what we mean by multimodality before going into morefancy terms.'
        f.search(input_fn=d, on_done=validate)
        f.search(input_fn=search_generator(data_path='data/photo-1.png'), read_mode='r', on_done=validate)
        f.search(input_fn=search_generator(data_path='data/blog2-pages-1.pdf'), read_mode='r', on_done=validate)
