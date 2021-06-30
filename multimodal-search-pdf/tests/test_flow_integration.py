__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import glob

import pytest
from click.testing import CliRunner

from jina import Flow, Document

from app import main


TEST_WORKSPACE = 'test-workspace'


def search_generator(data_path):
    d = Document()
    d.content = data_path
    yield d


def assert_result(resp):
    assert len(resp.docs) > 0, 'No docs returned'
    for doc in resp.docs:
        assert len(doc.matches) > 0, 'No matches returned'


@pytest.fixture(scope='session', autouse=True)
def index(tmpdir_factory):
    assert os.getcwd().endswith('multimodal-search-pdf'), \
        "Please execute the tests from the root directory: >>> pytest tests/"

    workspace = os.path.join(tmpdir_factory.getbasetemp(), 'test-workspace')
    assert not os.path.isdir(workspace), 'Directory ./test-workspace exists. Please remove before testing'
    os.environ['JINA_WORKSPACE'] = workspace

    runner = CliRunner()
    result = runner.invoke(main, ['-t', 'index'])
    assert result.stderr_bytes is None, f'Error messages found during indexing: {result.stderr}'

    assert os.path.isdir(workspace)
    index_files = glob.glob(os.path.join(workspace, '**', '*.json'), recursive=True)
    assert len(index_files) == 3, 'Expected three JSON files in the workspace'
    for _file in index_files:
        assert len(open(_file, 'r').readlines()) > 0, f'Json file {_file} is empty.'

    yield
    shutil.rmtree(workspace)


def test_query_multi_modal_pdf():
    f = Flow.load_config('flows/query.yml')
    with f:
        f.post(
            '/search',
            inputs=search_generator(data_path='toy_data/blog2-pages-1.pdf'),
            read_mode='r',
            on_done=assert_result
        )


def test_query_multi_modal_text():
    f = Flow.load_config('flows/query.yml')
    search_text = 'It makes sense to first define what we mean by multimodality before going into more fancy terms.'
    doc = Document(text=search_text)

    with f:
        f.post(
            '/search',
            inputs=doc,
            on_done=assert_result
        )


def test_query_multi_modal_image():
    f = Flow.load_config('flows/query.yml')
    with f:
        f.post(
            '/search',
            inputs=search_generator(data_path='toy_data/photo-1.png'),
            read_mode='r',
            on_done=assert_result
        )
