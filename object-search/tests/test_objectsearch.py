__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
from click.testing import CliRunner

sys.path.append('..')
from app import main


def config(tmpdir):
    os.environ['JINA_DATA_FILE'] = 'tests/test-data/*.jpg'
    os.environ['WORKDIR'] = os.path.join(tmpdir, 'workspace')


def test_object_search(tmpdir):
    config(tmpdir)
    runner = CliRunner()
    result = runner.invoke(main, ['-t', 'index', '-overwrite', 'True'])
    assert 'done in' in result.stdout
    assert result.stderr_bytes is None
    result = runner.invoke(main, ['-t', 'query', '-r', 'object', '-f', 'tests/test-data/dog-object.png'])
    assert 'matches of the type image/png are found' in result.stdout
    assert result.stderr_bytes is None
    result = runner.invoke(main, ['-t', 'query', '-r', 'original', '-f', 'tests/test-data/dog.jpg'])
    assert 'matches of the type image/jpeg are found' in result.stdout
    assert result.stderr_bytes is None
