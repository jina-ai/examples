__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__version__ = '0.0.1'

import json
import os
import sys

import click
from jina.flow import Flow

TOP_K = 3


def config():
    # parallel = 2 if task == 'index' else 1
    # os.environ['PARALLEL'] = str(parallel)
    os.environ['SHARDS'] = str(1)
    os.environ['WORKDIR'] = './workspace'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))


def call_api(url, payload=None, headers={'Content-Type': 'application/json'}):
    import requests
    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def extract_result(resp):
    result = []
    num_of_queries = []
    # resp.search.docs[0].matches
    # resp.search.docs[0].matches[0].score.value == 1
    for data in resp.search.docs:
        num_of_queries.append(data)
        for match in data.matches:
            match_label = match.tags['label']
            result.append(match_label)
    return result, num_of_queries


def search_done(resp):
    result, num_of_queries = extract_result(resp)
    print(result)
    temp = resp.search.docs[2]


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=100)
def main(task, num_docs):
    config()
    if task == 'index':
        workspace = os.environ['WORKDIR']
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
            print("hell")
    elif task == 'query':
        f = Flow.load_config('flows/query.yml')
        with f:
            f.block()
    elif task == 'dryrun':
        f = Flow.load_config('flows/query.yml')
        with f:
            f.search_files('data/Y--4gqARaEJE.wav', on_done=search_done)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query` or `dryrun`.')


if __name__ == '__main__':
    main()
