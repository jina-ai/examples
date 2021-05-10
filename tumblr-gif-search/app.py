__copyright__ = "Copyright (c) 2020 - 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
import click
import requests
from glob import glob

from jina.flow import Flow
from jina.logging.profile import TimeContext
from jina import Document
from jina.logging import default_logger as logger
from jina.clients.sugary_io import _input_lines


GIF_BLOB = 'data/*.gif'
SHARDS_DOC = 2
SHARDS_CHUNK_SEG = 2
SHARDS_INDEXER = 2
JINA_TOPK = 11
MAX_DOCS = int(os.environ.get('JINA_MAX_DOCS', 50))


def config():
    os.environ['SHARDS_DOC'] = str(SHARDS_DOC)
    os.environ['JINA_TOPK'] = str(JINA_TOPK)
    os.environ['SHARDS_CHUNK_SEG'] = str(SHARDS_CHUNK_SEG)
    os.environ['SHARDS_INDEXER'] = str(SHARDS_INDEXER)
    os.environ['JINA_WORKSPACE'] = './workspace'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def index(num_docs: int):
    f = Flow.load_config('flow-index.yml')
    num_docs = min(num_docs, len(glob(GIF_BLOB)))
    with f:
        with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
            f.index_files(GIF_BLOB, request_size=10, read_mode='rb', skip_dry_run=True, size=num_docs)


def query_restful():
    f = Flow.load_config('flow-query.yml')
    f.use_rest_gateway()

    # no perf measure, as it opens a REST api and blocks
    with f:
        f.block()


def index_restful(num_docs):
    f = Flow().load_config('flow-index.yml')

    with f:
        data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None))
        f.logger.info(f'Indexing {data_path}')
        url = f'http://0.0.0.0:{f.port_expose}/index'

        input_docs = _input_lines(
            filepath=data_path,
            size=num_docs,
            read_mode='r',
        )
        data_json = {'data': [Document(text=text).dict() for text in input_docs]}
        r = requests.post(url, json=data_json)
        if r.status_code != 200:
            raise Exception(f'api request failed, url: {url}, status: {r.status_code}, content: {r.content}')


# for test before put into docker
def dryrun():
    f = Flow().load_config('flow-index.yml')
    with f:
        pass


@click.command()
@click.option('--task', '-t',
              type=click.Choice(['index', 'index_restful', 'query_restful', 'dryrun'], case_sensitive=False))
@click.option('--num_docs_index', '-n', default=600)
def main(task, num_docs_index):
    config()
    workspace = os.environ['JINA_WORKSPACE']
    if 'index' in task:
        if os.path.exists(workspace):
            logger.error(
                f'\n +------------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                           | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                           | \
                    \n +------------------------------------------------------------------------------------+'
            )
            sys.exit(1)
    if task == 'index':
        index(num_docs_index)
    elif task == 'index_restful':
        index_restful(num_docs_index)
    elif task == 'query_restful':
        if not os.path.exists(workspace):
            logger.error(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
            sys.exit(1)
        query_restful()
    elif task == 'dryrun':
        dryrun()


if __name__ == '__main__':
    main()
