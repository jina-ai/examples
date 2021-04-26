__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__version__ = '0.0.1'

import json
import os
import sys

import click
import requests
from jina import Document
from jina.clients.sugary_io import _input_lines
from jina.flow import Flow
from jina.logging.profile import TimeContext

JINA_TOPK = 5


def config():
    os.environ['JINA_SHARDS'] = str(4)
    os.environ['JINA_WORKSPACE'] = './workspace'
    os.environ['JINA_DATA_FILE'] = 'data/*.wav'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))
    os.environ['JINA_TOPK'] = str(JINA_TOPK)


def call_api(url, payload=None, headers={'Content-Type': 'application/json'}):
    return requests.post(url, data=json.dumps(payload), headers=headers).json()

def index_restful(num_docs):
    f = Flow().load_config('flows/index.yml')

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
        with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
            r = requests.post(url, json=data_json)
            if r.status_code != 200:
                raise Exception(f'api request failed, url: {url}, status: {r.status_code}, content: {r.content}')


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=100)
def main(task, num_docs):
    config()
    if task == 'index':
        workspace = os.environ['JINA_WORKSPACE']
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
            sys.exit(1)

        f = Flow.load_config('flows/index.yml')
        with f:
            with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
                f.index_files('data/*.wav', batch_size=2, size=num_docs)
    elif task == 'index_restful':
        index_restful(num_docs)
    elif task == 'query':
        f = Flow.load_config('flows/query.yml')
        with f:
            # no perf measurement here, as it opens the REST API and blocks
            f.block()
    elif task == 'dryrun':
        f = Flow.load_config('flows/query.yml')
        with f:
            pass
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query` or `dryrun`.')


if __name__ == '__main__':
    main()
