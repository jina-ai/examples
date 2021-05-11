__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
from click.testing import CliRunner

sys.path.append('..')
from app import main


def config(tmpdir):
    os.environ['JINA_DATA_FILE'] = os.path.join(os.path.dirname(__file__), 'toy-input.txt')
    os.environ['JINA_WORKSPACE'] = os.path.join(tmpdir, 'workspace')


# TODO: query_restful is not covered.
def test_wikipediasearch_index(tmpdir):
    config(tmpdir)
    runner = CliRunner()
    result = runner.invoke(main, ['-t', 'index'])
    assert 'done in' in result.stdout
    result = runner.invoke(main, ['-t', 'query', '-k', '100'], input='Their land was taken back by the Spanish Crown')
    assert 'California became part of the United States' in result.stdout
    assert '> 49(' in result.stdout  # Only 50 docs in the toy-input.txt
