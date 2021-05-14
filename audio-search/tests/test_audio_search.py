__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
from sys import platform
import pytest

sys.path.append('..')
from app import main
from click.testing import CliRunner


def config(tmpdir):
    os.environ['JINA_WORKSPACE'] = os.path.join(tmpdir, 'workspace')
    if platform == "linux":
        os.system('sudo apt-get install libsndfile1')


@pytest.fixture
def download_model():
    os.system('./download_model.sh')


def test_audio_search(tmpdir, download_model):
    config(tmpdir)
    runner = CliRunner()
    result = runner.invoke(main, ['-t', 'index'])
    assert 'done in' in result.stdout
    result = runner.invoke(main, ['-t', 'query'])
    assert result.stderr_bytes is None
