import os
import glob
import shutil
from functools import partial
from pathlib import Path
from typing import Optional

import click
from jina import DocumentArray, Document, Flow

from executors import TimeSegmenter, Wav2MelCrafter, DebugExecutor
from helper import report_results, write_html, create_query_audios, create_docs, logger


def config():
    os.environ.setdefault('JINA_WORKSPACE', str(Path(__file__).parent / 'workspace'))
    os.environ.setdefault('JINA_DATA_FILE', str(Path(__file__).parent / 'data' / 'mp3'))
    os.environ.setdefault(
        'JINA_WORKSPACE_MOUNT',
        f'{os.environ.get("JINA_WORKSPACE")}:/workspace/workspace',
    )


def index(workspace: Path, data_dir: Path, flow: Flow):
    if workspace.exists():
        shutil.rmtree(workspace)
    with flow:
        flow.post(
            '/index', inputs=create_docs(os.path.join(data_dir, 'index', '*.mp3'))
        )


def search(
    workspace: Path,
    data_dir: Path,
    flow: Flow,
    threshold: Optional[float],
    top_k: int,
    num_queries: int,
):
    if not workspace.exists():
        raise FileNotFoundError(
            f'The directory {workspace} does not exist. Please index first via `python app.py index`'
        )

    with flow:
        create_query_audios(num_queries, data_dir)
        responses = flow.post(
            '/search',
            inputs=create_docs(os.path.join(data_dir, 'query', '*.mp3')),
            return_results=True,
        )

    result_html, accuracy = report_results(responses, threshold, top_k)
    write_html(str(workspace / 'demo.html'), result_html, accuracy, top_k)


def validate_threshold(
    ctx: click.core.Option, param: click.core.Context, threshold: Optional[float]
):
    if threshold is not None and not 0 <= threshold <= 1:
        raise click.BadParameter('threshold should be between 0 and 1')


@click.command()
@click.argument('operation', type=click.Choice(['index', 'search']))
@click.option(
    '--segmenter',
    '-s',
    default='vad',
    type=click.Choice(['time', 'vad']),
    help='Specify the segmenter to use (i.e. vad or time)',
)
@click.option(
    '--encoder',
    '-e',
    default='vgg',
    type=click.Choice(['vgg', 'clip']),
    help='Specify the encoder to use (i.e. vgg or clip)',
)
@click.option(
    '--threshold',
    '-t',
    default=None,
    type=float,
    callback=validate_threshold,
    help='Specify the distance threshold for matching (between 0 to 1)',
)
@click.option('--top_k', '-k', default=5, type=int, help='Specify top k for matching')
@click.option(
    '--num_queries',
    '-n',
    default=20,
    type=int,
    help='Specify the number of querys to match',
)
def cli(
    operation: str,
    segmenter: str,
    encoder: str,
    threshold: Optional[float],
    top_k: int,
    num_queries: int,
):
    config()

    data_dir = Path(os.environ["JINA_DATA_FILE"])
    workspace = Path(os.environ["JINA_WORKSPACE"])
    logger.info(f'data directory path: {data_dir}')
    logger.info(f'workspace path: {workspace}')

    segmenter_uses_with = {'chunk_duration': 2.5} if segmenter == 'time' else {}
    segmenter = {'time': TimeSegmenter, 'vad': 'jinahub://VADSpeechSegmenter'}[
        segmenter
    ]

    encoder = {
        'clip': 'jinahub://AudioCLIPEncoder',
        'vgg': 'jinahub://VGGishAudioEncoder',
    }[encoder]

    flow = (
        Flow()
        .add(
            uses=segmenter,
            uses_metas={'workspace': str(workspace)},
            uses_with=segmenter_uses_with,
        )
        .add(uses=Wav2MelCrafter)
        .add(uses=encoder, uses_with={'default_traversal_paths': ['c']})
        # Since matched chunks may come from the same top level query doc,
        # we set default_top_k to top_k * 2 so that we have sufficient information to
        # determine the true top k matches as a quick workaround.
        .add(
            uses='jinahub://SimpleIndexer',
            uses_with={
                'index_file_name': 'simple_indexer',
                'default_traversal_paths': ['c'],
                'default_top_k': top_k * 2,
            },
            uses_metas={'workspace': str(workspace)},
        )
        .add(uses=DebugExecutor)
        .add(uses='jinahub://SimpleRanker', uses_metas={'workspace': str(workspace)})
    )

    {
        'index': index,
        'search': partial(
            search, threshold=threshold, top_k=top_k, num_queries=num_queries
        ),
    }[operation](workspace, data_dir, flow)


if __name__ == '__main__':
    cli()
