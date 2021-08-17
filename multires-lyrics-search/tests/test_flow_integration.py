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
    os.environ.setdefault('JINA_WORKSPACE_MOUNT',
                          f'{os.environ.get("JINA_WORKSPACE")}:/workspace/workspace')
    os.environ.setdefault('JINA_PORT', str(45678))

    runner = CliRunner()
    result = runner.invoke(main, ['-t', 'index', '-n', '100'])
    assert result.stderr_bytes is None, f'Error messages found during indexing: {result.stderr}'

    assert os.path.isdir(workspace)
    index_files = get_files_with_patterns(workspace, ['*.bin', '*.lmdb', '*.lmdb-lock'])
    assert len(index_files) == 4, 'Expected three files in the workspace'
    for _file in index_files:
        assert os.path.getsize(_file) > 0, f'File {_file} is empty.'

    yield
    # shutil.rmtree(workspace) Not possible due to docker sudo rights


def test_query_text(tmpdir_factory):
    def assert_result(response):
        docs = response.docs
        # check number of results
        assert len(docs) == 1
        assert len(docs[0].chunks) == 2
        parent_docs = docs[0].matches
        parent_ids = parent_docs.get_attributes('id')
        assert len(parent_docs) > 0
        for chunk in docs[0].chunks:
            assert len(chunk.matches) == 5  # top_k = 5
            match_ids = chunk.matches.get_attributes('id')
            assert len(match_ids) == len(list(set(match_ids)))
            for match in chunk.matches:
                assert match.text is not None
                assert match.location is not None
                assert match.parent_id in parent_ids
                assert match.text in parent_docs[parent_ids.index(match.parent_id)].text

    flow = Flow.load_config('flows/query.yml')
    with flow:
        search_text = 'looked through every window then. hello world.'
        doc = Document(content=search_text, mime_type='text/plain')
        response = flow.post('/search', inputs=doc, parameters={'top_k': 5}, return_results=True)
        assert_result(response[0])
