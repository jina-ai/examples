__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
from click.testing import CliRunner

sys.path.append('..')
from app import main


def config(tmpdir):
    os.environ['JINA_WORKSPACE'] = os.path.join(tmpdir, 'workspace')


def test_wikipedia_sentences(tmpdir):
    config(tmpdir)
    runner = CliRunner()
    result = runner.invoke(main, ['-t', 'index', '--num_docs', 10])
    assert "done in" in result.stdout
    assert result.stderr_bytes is None
    result = runner.invoke(main, ['-t', 'query', '--num_docs', 10])
    print(result.stdout)
    assert result.stderr_bytes is None
