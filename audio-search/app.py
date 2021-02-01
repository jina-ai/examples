__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__version__ = '0.0.1'

import json
import os
import sys

import click
from jina.flow import Flow

JINA_TOPK = 5


def config():
    os.environ['JINA_SHARDS'] = str(4)
    os.environ['JINA_WORKSPACE'] = './workspace'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))
    os.environ['JINA_TOPK'] = str(JINA_TOPK)


def call_api(url, payload=None, headers={'Content-Type': 'application/json'}):
    import requests
    return requests.post(url, data=json.dumps(payload), headers=headers).json()


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
            f.index_files('data/*.wav', batch_size=2, size=num_docs)
    elif task == 'query':
        f = Flow.load_config('flows/query.yml')
        with f:
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
