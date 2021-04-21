__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__version__ = '0.0.1'

import csv
import os
import sys
import itertools
import click
import requests

from jina.flow import Flow
from jina import Document
from jina.clients.sugary_io import _input_lines
from jina.logging.profile import TimeContext


def config():
    parallel = 2 if sys.argv[1] == 'index' else 1

    os.environ.setdefault('JINA_MAX_DOCS', '100')
    os.environ.setdefault('JINA_PARALLEL', str(parallel))
    os.environ.setdefault('JINA_SHARDS', str(4))
    os.environ.setdefault('JINA_WORKSPACE', './workspace')
    os.environ.setdefault('JINA_DATA_FILE', 'toy-data/lyrics-toy-data1000.csv')
    os.environ['JINA_WORKDIR'] = './workspace'
    os.makedirs(os.environ['JINA_WORKDIR'], exist_ok=True)
    os.environ.setdefault('JINA_PORT', str(65481))


def input_fn():
    lyrics_file = os.environ.setdefault(
        'JINA_DATA_PATH', 'toy-data/lyrics-toy-data1000.csv'
    )
    docs = []
    with open(lyrics_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in itertools.islice(reader, int(os.environ['JINA_MAX_DOCS'])):
            if row[-1] == 'ENGLISH':
                with Document() as d:
                    d.tags['ALink'] = row[0]
                    d.tags['SName'] = row[1]
                    d.tags['SLink'] = row[2]
                    d.text = row[3]
                docs.append(d)

    return docs


# for index
def index():
    f = Flow.load_config('flows/index.yml')
    with f:
        input_docs = input_fn()
        with TimeContext(f'QPS: indexing {len(input_docs)}', logger=f.logger):
            f.index(input_docs, request_size=8)


# for search
def query():
    f = Flow.load_config('flows/query.yml')

    with f:
        f.block()


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
        print(f'#### {len(data_json["data"])}')
        r = requests.post(url, json=data_json)
        if r.status_code != 200:
            raise Exception(f'api request failed, url: {url}, status: {r.status_code}, content: {r.content}')


def query_restful():
    f = Flow().load_config("flows/query.yml")
    f.use_rest_gateway()
    with f:
        f.block()


def dryrun():
    f = Flow().load_config("flows/index.yml")
    with f:
        pass


@click.command()
@click.option('--task', '-t',
              type=click.Choice(['index', 'query', 'index_restful', 'query_restful', 'dryrun'], case_sensitive=False))
@click.option('--num_docs_index', '-n', default=600)
def main(task, num_docs_index):
    config()
    workspace = os.environ["JINA_WORKSPACE"]

    if task == 'index':
        config()
        workspace = os.environ['JINA_WORKDIR']
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
        index()
    elif task == 'index_restful':
        index_restful(num_docs_index)
    elif task == 'query':
        config()
        query()
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
