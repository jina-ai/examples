import os
import glob
import logging
import shutil
from functools import partial
from pathlib import Path

import click
from jina import DocumentArray, Document, Flow

from executors import TimeSegmenter, Wav2MelCrafter, DebugExecutor
from helper import report_results, write_html, TOP_K, create_query_audios, create_docs

cur_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(cur_dir, 'data', 'mp3')


def index(workspace, flow):
    if workspace.exists():
        shutil.rmtree(workspace)
    documents = create_docs(os.path.join(data_folder, 'index', '*.mp3'), None)
    with flow:
        flow.post('/index', inputs=documents)


def search(workspace, flow, threshold):
    if not workspace.exists():
        raise FileNotFoundError(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')

    create_query_audios(20)
    query = create_docs(os.path.join(data_folder, 'query', '*.mp3'), None)
    with flow:
        flow.post('/search', inputs=query,
                  on_done=lambda resp: report_results(resp, threshold))
    write_html(str(workspace / 'demo.html'))


def validate_threshold(ctx, param, threshold):
    if threshold is not None and not 0 <= threshold <= 1:
        raise click.BadParameter('threshold should be between 0 and 1')


@click.command()
@click.argument('operation', type=click.Choice(['index', 'search']))
@click.option(
        '--segmenter',
        '-s',
        default='vad',
        type=click.Choice(['time', 'vad']),
        help='Specify the segmenter to use (i.e. vad or time)')
@click.option(
        '--encoder',
        '-e',
        default='vgg',
        type=click.Choice(['vgg', 'clip']),
        help='Specify the encoder to use (i.e. vgg or clip)')
@click.option(
        '--threshold',
        '-t',
        default=None,
        type=float,
        callback=validate_threshold,
        help='Specify the distance threshold for matching (between 0 to 1)')
def cli(operation, segmenter, encoder, threshold):
    workspace = Path(cur_dir) / 'workspace'
    segmenter_uses_with = {'chunk_duration': 20} if segmenter == 'time' else {}
    segmenter = {'time': TimeSegmenter, 'vad': 'jinahub://VADSpeechSegmenter'}[segmenter]
    encoder = {'clip': 'jinahub://AudioCLIPEncoder', 'vgg': 'jinahub://VGGishAudioEncoder'}[encoder]

    flow = (Flow()
         .add(uses=segmenter, uses_metas={'workspace': str(workspace)}, uses_with=segmenter_uses_with)
         .add(uses=Wav2MelCrafter)
         .add(uses=encoder, uses_with={'default_traversal_paths': ['c']})
          # Since matched chunks may come from the same top level query doc,
          # we set default_top_k to TOP_K * 2 so that we have sufficient information to
          # determine the true top k matches
         .add(uses='jinahub://SimpleIndexer',
             uses_with={'index_file_name': 'simple_indexer', 'default_traversal_paths': ['c'],
                        'default_top_k': TOP_K * 2})
         .add(uses=DebugExecutor)
         .add(uses='jinahub://SimpleRanker',
              uses_metas={'workspace': str(workspace)}))

    {'index': index, 'search': partial(search, threshold=threshold)}[operation](workspace, flow)


if __name__ == '__main__':
    cli()
