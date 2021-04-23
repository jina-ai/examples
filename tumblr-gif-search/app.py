__copyright__ = "Copyright (c) 2020 - 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
from glob import glob
import click
import requests
import matplotlib.pyplot as plt
from collections import defaultdict


import urllib.request
import gzip
import numpy as np
import webbrowser
import random

from jina.flow import Flow
from jina import Document
from jina.clients.sugary_io import _input_files
from jina.clients.sugary_io import _input_lines


GIF_BLOB = 'data/*.gif'
# TODO test w 2
SHARDS_DOC = 2
SHARDS_CHUNK_SEG = 2
SHARDS_INDEXER = 2
JINA_TOPK = 11


def config():
    os.environ['SHARDS_DOC'] = str(SHARDS_DOC)
    os.environ['JINA_TOPK'] = str(JINA_TOPK)
    os.environ['SHARDS_CHUNK_SEG'] = str(SHARDS_CHUNK_SEG)
    os.environ['SHARDS_INDEXER'] = str(SHARDS_INDEXER)
    os.environ['JINA_WORKSPACE'] = './workspace'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


# for index
def index():
    config()
    f = Flow.load_config('flow-index.yml')

    with f:
        f.index_files(GIF_BLOB, request_size=10, read_mode='rb', skip_dry_run=True)


# for search
def query():
    config()
    f = Flow.load_config('flow-query.yml')

    with f:
        # waiting for input via REST gateway
        f.block()


def index_restful(num_docs):
    config()
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


def query_restful():
    config()
    f = Flow().load_config("flow-query.yml")
    f.use_rest_gateway()
    with f:
        f.block()

# for test before put into docker
def dryrun():
    f = Flow().load_config("flow-index.yml")
    with f:
        pass


@click.command()
@click.option('--task', '-t',
              type=click.Choice(['index', 'query', 'index_restful', 'query_restful', 'dryrun'], case_sensitive=False))
@click.option('--num_docs_query', '-n', default=100)
@click.option('--num_docs_index', '-n', default=600)
def main(task, num_docs_query, num_docs_index):
    config(task)

    workspace = os.environ["JINA_WORKSPACE"]
    if 'index' in task:
        if os.path.exists(workspace):
            print(
                f'\n +------------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                           | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                           | \
                    \n +------------------------------------------------------------------------------------+'
            )
            sys.exit(1)

    print(f'### task = {task}')
    if task == 'index':
        config(task)
        workspace = os.environ['JINA_WORKDIR']
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
        index(num_docs_index)
    elif task == 'index_restful':
        index_restful(num_docs_index)
    elif task == 'query':
        config(task)
        query(num_docs_query)
    elif task == 'query_restful':
        if not os.path.exists(workspace):
            print(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
        query_restful()
    elif task == 'dryrun':
        dryrun()
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()