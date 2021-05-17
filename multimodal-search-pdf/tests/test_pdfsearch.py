__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

sys.path.append('..')
from app import main
from click.testing import CliRunner


def config(tmp_dir):
    os.environ["JINA_WORKSPACE"] = os.path.join(tmp_dir, os.environ.get("JINA_WORKSPACE", "workspace"))


def test_multimodal_search_pdf(tmpdir):
    config(tmpdir)
    runner = CliRunner()
    result = runner.invoke(main, ['-t', 'index'])
    assert 'done in' in result.stdout
    assert '🔴' not in result.stdout
    assert '⚪' not in result.stdout
    result = runner.invoke(main, ['-t', 'query_text'])
    assert result.stderr_bytes is None
    result = runner.invoke(main, ['-t', 'query_image'])
    assert result.stderr_bytes is None
    result = runner.invoke(main, ['-t', 'query_pdf'])
    assert result.stderr_bytes is None
    # TODO: `query_restful` is not covered
