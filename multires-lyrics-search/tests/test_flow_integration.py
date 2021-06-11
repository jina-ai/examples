__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import glob
from typing import List
from click.testing import CliRunner

import pytest
from jina import Flow, Document

from app import main


def get_files_with_patterns(directory: str, match_patterns: List[str]) -> List[str]:
    """
    Returns all files from directory and subdirectories that match any of the patterns in the list.
    The returned list will only contain unique items.

    :param directory: Path to the directory
    :param match_patterns: A list of expressions to match the files against. E.g. `*.json`
    :return: List of matched files.
    """
    index_files = []
    for pattern in match_patterns:
        index_files += list(glob.glob(os.path.join(directory, '**', pattern), recursive=True))
    return list(set(index_files))


@pytest.fixture(scope='session', autouse=True)
def index(tmpdir_factory):
    """
    This fixtures runs automatically once before each test session.
    It indexes a small set of files into a test workspace and checks that the indexing
    completes correctly.

    Other tests can use the created workspace and test queries against it.
    """
    assert os.getcwd().endswith('multires-lyrics-search'), \
        "Please execute the tests from the root directory: >>> pytest tests/"

    workspace = os.path.join(tmpdir_factory.getbasetemp(), 'test-workspace')
    assert not os.path.isdir(workspace), 'Directory ./test-workspace exists. Please remove before testing'
    os.environ['JINA_WORKSPACE'] = workspace

    runner = CliRunner()
    result = runner.invoke(main, ['-t', 'index', '-n', '5'])
    assert result.stderr_bytes is None, f'Error messages found during indexing: {result.stderr}'

    assert os.path.isdir(workspace)
    index_files = get_files_with_patterns(workspace, ['*.json', '*.binary'])
    assert len(index_files) == 2, 'Expected three files in the workspace'
    for _file in index_files:
        assert os.path.getsize(_file) > 0, f'File {_file} is empty.'

    yield
    shutil.rmtree(workspace)


def test_query_text():
    def assert_result(response):
        docs = response.docs

        # check number of results
        num_results = sum([len(d.matches) for d in response.docs])
        assert num_results == 5, f'With top_k=5, expected five results but got {num_results}'

        # check uniqueness of results
        match_ids = docs.traverse_flat('m').get_attributes('id')
        assert len(match_ids) == len(list(set(match_ids)))

        # check content of results
        for match in docs.traverse_flat('m'):
            assert match.text is not None
            assert match.location is not None

    flow = Flow.load_config('flows/query.yml')
    with flow:
        search_text = 'looked through every window then'
        doc = Document(content=search_text, mime_type='text/plain')
        flow.post('/search', inputs=doc, on_done=assert_result)
