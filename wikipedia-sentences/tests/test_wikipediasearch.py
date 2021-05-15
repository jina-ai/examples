__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
import pytest
from click.testing import CliRunner

sys.path.append('..')
from app import main


def config(tmpdir):
    os.environ['JINA_DATA_FILE'] = os.path.join(os.path.dirname(__file__), 'toy-input.txt')
    os.environ['JINA_WORKSPACE'] = os.path.join(tmpdir, 'workspace')


# TODO: query_restful is not covered.
@pytest.mark.parametrize('task_para',
                         [('index',
                           'Their land was taken back by the Spanish Crown',
                           'California became part of the United States',
                           '> 49('),
                          ('index_incremental',
                           'Andrea Kremer',
                           'multi-Emmy Award Winning American',
                           '> 99(')
                          ])
def test_wikipediasearch_index(tmpdir, task_para):
    task_str, input_str, output_str, last_str = task_para
    config(tmpdir)
    runner = CliRunner()
    result = runner.invoke(main, ['-t', task_str])
    assert 'done in' in result.stdout
    result = runner.invoke(main, ['-t', 'query', '-k', '200'], input=input_str)
    assert output_str in result.stdout
    assert last_str in result.stdout
