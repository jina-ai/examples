__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

sys.path.append('..')
from app import main


def config(tmpdir):
    shards_encoder = 1
    os.environ['JINA_SHARDS_ENCODER'] = os.getenv('JINA_SHARDS_ENCODER', str(shards_encoder))
    os.environ['JINA_WORKDIR'] = os.path.join(tmpdir, 'workspace')


def test_fashion_example(tmpdir):
    config(tmpdir)
    from click.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(main, ['-t', 'index'])
    assert 'done in' in result.stdout
    runner.invoke(main, ['-t', 'query'])
    assert os.path.exists(os.path.join(os.environ.get('JINA_WORKDIR'), 'hello-world.html'))
