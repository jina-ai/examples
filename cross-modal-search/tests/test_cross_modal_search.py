import os
import sys
sys.path.append('..')
from app import main
from click.testing import CliRunner


def config(tmpdir):
    os.environ['JINA_WORKSPACE'] = os.path.join(tmpdir, 'workspace')


def test_cross_modal_search(tmpdir):
    config(tmpdir)
    runner = CliRunner()
    result = runner.invoke(main, ['-t', 'index'])
    assert 'done in' in result.stdout
    assert result.stderr_bytes is None
    result = runner.invoke(main, ['-t', 'query'])
    assert result.stderr_bytes is None
