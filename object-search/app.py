__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import sys
from glob import glob

import click
from jina.flow import Flow
from jina import Document
from jina.logging.profile import TimeContext

from jina.logging import JinaLogger

MAX_DOCS = os.environ.get('MAX_DOCS', 16)
BATCH_SIZE = 16

logger = JinaLogger('object-search')


def config():
    os.environ['JINA_DATA_FILE'] = os.environ.get('JINA_DATA_FILE', 'data/**/*.jpg')
    os.environ['PARALLEL'] = '1'
    os.environ['SHARDS'] = '1'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))
    os.environ['WORKDIR'] = os.environ.get('JINA_WORKDIR', './workspace')


def index(data_path, batch_size, num_docs: int):
    f = Flow.load_config('flow-index.yml')
    num_docs = min(num_docs, len(glob(data_path)))
    with f:
        with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
            f.index_files(data_path, request_size=batch_size, read_mode='rb', size=num_docs)


def get_image(resp):
    match_type = resp.search.docs[0].matches[0].mime_type
    print(f'{len(resp.search.docs[0].matches)} matches of the type {match_type} are found')


def _query(flow_fn, query_fn):
    f = Flow.load_config(flow_fn)
    f.use_grpc_gateway()
    with f:
        with TimeContext(f'QPS: query ', logger=f.logger):
            # read image file and load into uri
            d = Document(uri=query_fn)
            d.convert_uri_to_data_uri()
            f.search(inputs=[d, ], on_done=get_image)


def query(return_image, query_fn):
    _query(f'flow-query-{return_image}.yml', query_fn)


def query_restful(return_image):
    f = Flow().load_config(f'flow-query-{return_image}.yml')
    f.use_rest_gateway()
    with f:
        f.block()


@click.command()
@click.option(
    '--task',
    '-t',
    type=click.Choice(['index', 'query', 'query_restful'], case_sensitive=False),
)
@click.option(
    '--return_image',
    '-r',
    default='original',
    type=click.Choice(['original', 'object'], case_sensitive=False)
)
@click.option('--num_docs', '-n', default=MAX_DOCS)
@click.option('--batch_size', '-b', default=BATCH_SIZE)
@click.option('--overwrite_workspace', '-overwrite', default=True)
@click.option('--query_file', '-f', default=None)
def main(task, return_image, num_docs, batch_size, overwrite_workspace, query_file):
    config()
    workspace = os.environ['WORKDIR']
    data_path = os.environ['JINA_DATA_FILE']
    if task == 'index' and os.path.exists(workspace):
        if not overwrite_workspace:
            logger.info(
                f'\n +------------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                           | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                           | \
                    \n +------------------------------------------------------------------------------------+'
            )
            sys.exit(1)
        logger.info('deleting workspace...')
        shutil.rmtree(workspace)

    if task == 'index':
        logger.info(f'indexing {data_path}')
        index(data_path, batch_size, num_docs)

    if 'query' in task and not os.path.exists(workspace):
        logger.info(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
        sys.exit(1)

    if task == 'query':
        query(return_image, query_file)

    if task == 'query_restful':
        query_restful(return_image)


if __name__ == '__main__':
    main()
