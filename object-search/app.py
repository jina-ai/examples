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
from jina.logging import default_logger as logger
from jina.logging.profile import TimeContext

MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 50))
IMAGE_SRC = 'data/f8k/images/*.jpg'


def config():
    os.environ["JINA_DATA_FILE"] = os.environ.get("JINA_DATA_FILE", IMAGE_SRC)
    os.environ['PARALLEL'] = str(1)
    os.environ['SHARDS'] = str(1)
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))
    os.environ['WORKDIR'] = './workspace'


def index(num_docs: int):
    f = Flow.load_config('flow-index.yml')
    num_docs = min(num_docs, len(glob(IMAGE_SRC)))
    with f:
        with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
            f.index_files(IMAGE_SRC, request_size=10, read_mode='rb', size=num_docs)


def index_restful(num_docs):
    f = Flow().load_config('flow-index.yml')

    with f:
        data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None))
        print(f'Indexing {data_path}')
        url = f'http://0.0.0.0:{f.port_expose}/index'

        input_docs = _input_lines(
            filepath=data_path,
            size=num_docs,
            read_mode='r',
        )
        data_json = {'data': [Document(text=text).dict() for text in input_docs]}
        print(f'#### {len(data_json["data"])}')
        r = requests.post(url, json=data_json)
        if r.status_code != 200:
            raise Exception(f'api request failed, url: {url}, status: {r.status_code}, content: {r.content}')


def query_restful(return_image):
    f = Flow().load_config(f'flow-query-{return_image}.yml')
    f.use_rest_gateway()
    with f:
        f.block()


def dryrun():
    f = Flow().load_config("flow-index.yml")
    with f:
        pass


@click.command()
@click.option(
    '--task',
    '-t',
    type=click.Choice(['index', 'index-restful', 'query-restful', 'dry'], case_sensitive=False))
@click.option(
    '--return_image',
    '-r',
    default='original',
    type=click.Choice(['original', 'object'], case_sensitive=False))
@click.option('--num_docs', '-n', default=MAX_DOCS)
def main(task: str, return_image: str, num_docs: int):
    config()
    workspace = os.environ['WORKDIR']
    if 'index' in task:
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
            sys.exit(1)
    if task == 'index':
        index(num_docs)
    if task == 'index-restful':
        index_restful(num_docs)
    if task == 'query-restful':
        if not os.path.exists(workspace):
            print(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
            sys.exit(1)
        query(return_image)
    if task == 'dry':
        dryrun()


if __name__ == '__main__':
    main()
