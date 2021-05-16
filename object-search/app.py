__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import sys
from glob import glob
import requests

import click
from jina.flow import Flow
from jina import Document
from jina.clients.sugary_io import _input_lines
from jina.logging.profile import TimeContext

from jina.logging import JinaLogger

MAX_DOCS = os.environ.get('MAX_DOCS', 16)
IMAGE_SRC = 'data/**/*.jpg'
BATCH_SIZE = 16

logger = JinaLogger('object-search')


def config():
    os.environ['JINA_DATA_FILE'] = os.environ.get('JINA_DATA_FILE', IMAGE_SRC)
    os.environ['PARALLEL'] = '1'
    os.environ['SHARDS'] = '1'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))
    os.environ['WORKDIR'] = './workspace'


def index(num_docs: int):
    f = Flow.load_config('flow-index.yml')
    num_docs = min(num_docs, len(glob(IMAGE_SRC)))
    with f:
        with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
            f.index_files(IMAGE_SRC, request_size=10, read_mode='rb', size=num_docs)


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
    '--return_image', '-r', default='original', type=click.Choice(['original', 'object'], case_sensitive=False)
)
@click.option('--data_path', '-p', default=IMAGE_SRC)
@click.option('--num_docs', '-n', default=MAX_DOCS)
@click.option('--batch_size', '-b', default=BATCH_SIZE)
@click.option('--overwrite_workspace', '-overwrite', default=True)
def main(task, return_image, data_path, num_docs, batch_size, overwrite_workspace):
    config()
    workspace = os.environ['WORKDIR']
    if 'index' in task and os.path.exists(workspace):
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

    if 'query' in task and not os.path.exists(workspace):
        logger.info(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
        sys.exit(1)

    if task == 'index':
        f = Flow.load_config('flow-index.yml')
        with f:
            f.index_files(data_path, batch_size=batch_size, read_mode='rb', size=num_docs)
    elif task == 'query':
        f = Flow.load_config(f'flow-query-{return_image}.yml')
        with f:
            f.block()
    elif task == 'query_restful':
        query_restful(return_image)


if __name__ == '__main__':
    main()
