import glob
import os
import shutil

import pytest
from click.testing import CliRunner
from app import cli
from pathlib import Path


@pytest.mark.parametrize('segmenter', ['vad', 'time'])
@pytest.mark.parametrize('encoder', ['vgg'])
def test_exec(tmp_path, segmenter, encoder):
    assert os.getcwd().endswith(
        'audio-to-audio-search'
    ), "Please execute the tests from the root directory: >>> pytest tests/"
    os.environ['JINA_DATA_FILE'] = os.path.join('tests', 'data', 'mp3')
    workspace = os.environ['JINA_WORKSPACE'] = os.path.join(tmp_path, 'workspace')
    os.environ['JINA_WORKSPACE_MOUNT']= f'{workspace}:/workspace/workspace'
    runner = CliRunner()
    _test_index(runner, workspace, segmenter, encoder)
    _test_query(runner, segmenter, encoder)


def _test_index(runner, workspace, segmenter, encoder):
    result = runner.invoke(cli, ['index', '-s', segmenter, '-e', encoder])
    assert result.exception is None
    assert result.exit_code == 0
    assert Path(workspace).is_dir()
    assert (
        len(set(glob.glob(os.path.join(workspace, '**', '*.bin'), recursive=True))) == 2
    )


def _test_query(runner, segmenter, encoder):
    # test error case: query more docs than indexed
    result = runner.invoke(cli, ['search', '-s', segmenter, '-e', encoder, '-n', 10])

    with pytest.raises(
        FileNotFoundError,
        match='cannot find sufficient index audios clips. '
        'Number of index audio clips found: 5, number of requested query docs: 10',
    ):
        assert result.exception is not None
        raise result.exception

    assert result.exit_code != 0
    result = runner.invoke(cli, ['search', '-s', segmenter, '-e', encoder, '-n', 3])
    assert result.exception is None
    assert result.exit_code == 0
