__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import sys
import requests

import click
from jina.flow import Flow
from jina import Document
from jina.clients.sugary_io import _input_lines
from jina.logging import default_logger as logger


num_docs = os.environ.get('MAX_DOCS', 16)
data_path = 'data/**/*.jpg'
batch_size = 16


def clean_workdir():
    if os.path.exists(os.environ['WORKDIR']):
        shutil.rmtree(os.environ['WORKDIR'])
        logger.warning('Workspace deleted')


def config():
    parallel = 1 if sys.argv[1] == 'index' else 1
    shards = 1

    os.environ['PARALLEL'] = str(parallel)
    os.environ['SHARDS'] = str(shards)
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_DATA_FILE'] = os.environ.get('JINA_DATA_FILE', 'data/**/*.jpg')
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


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
    '-task',
    '-t',
    type=click.Choice(['index', 'query', 'index_restful', 'query_restful', 'dryrun'], case_sensitive=False),
)
@click.option(
    '--return_image', '-r', default='original', type=click.Choice(['original', 'object'], case_sensitive=False)
)
@click.option('--data_path', '-p', default=data_path)
@click.option('--num_docs', '-n', default=num_docs)
@click.option('--batch_size', '-b', default=batch_size)
@click.option('--overwrite_workspace', '-overwrite', default=True)
def main(task, return_image, data_path, num_docs, batch_size, overwrite_workspace):
    config()
    workspace = os.environ['WORKDIR']
    if 'index' in task:
        if os.path.exists(workspace):
            if overwrite_workspace:
                clean_workdir()
            else:
                print(
                    f'\n +------------------------------------------------------------------------------------+ \
                        \n |                                   🤖🤖🤖                                           | \
                        \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                        \n |                                   🤖🤖🤖                                           | \
                        \n +------------------------------------------------------------------------------------+'
                )
                sys.exit(1)

    elif 'query' in task:
        if not os.path.exists(workspace):
            print(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")

    if task == 'index':
        f = Flow.load_config('flow-index.yml')
        with f:
            f.index_files(data_path, batch_size=batch_size, read_mode='rb', size=num_docs)
    elif task == 'index_restful':
        index_restful(num_docs)
    elif task == 'query':
        f = Flow.load_config(f'flow-query-{return_image}.yml')
        with f:
            f.block()
    elif task == 'query_restful':
        query_restful(return_image)
    elif task == 'dryrun':
        dryrun()


if __name__ == '__main__':
    main()
