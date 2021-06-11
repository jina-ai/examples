__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__version__ = '0.0.1'

import os
import sys
import click
import requests

from jina import Flow, Document
from helper import input_generator
from jina.logging.predefined import default_logger as logger


def config():
    os.environ.setdefault('JINA_WORKSPACE', './workspace')
    if os.path.exists('lyrics-data/lyrics-data.csv'):
        os.environ.setdefault('JINA_DATA_FILE', 'lyrics-data/lyrics-data.csv')
    else:
        os.environ.setdefault('JINA_DATA_FILE', 'lyrics-data/lyrics-toy-data1000.csv')
    os.environ.setdefault('JINA_PORT', str(45678))


# for index
def index(num_docs):
    flow = Flow.load_config('flows/index.yml')
    with flow:
        input_docs = input_generator(num_docs=num_docs)
        flow.post(on='/index', inputs=input_docs, request_size=10)


def index_restful(num_docs):
    f = Flow().load_config('flows/index.yml')
    f.use_rest_gateway()
    with f:
        data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None))
        f.logger.info(f'Indexing {data_path}')
        url = f'http://0.0.0.0:{f.port_expose}/index'

        input_docs = input_generator(num_docs=num_docs)
        data_json = {'data': [doc.dict() for doc in input_docs]}
        r = requests.post(url, json=data_json)
        if r.status_code != 200:
            raise Exception(f'api request failed, url: {url}, status: {r.status_code}, content: {r.content}')


# for search
def query():
    f = Flow.load_config('flows/query.yml')
    with f:
        f.block()


def query_text():
    def print_result(response):
        print(response.docs[0])
        print(response.docs[0].matches)

        print(f'Total matches {sum([len(d.matches) for d in response.docs])}')

    f = Flow.load_config('flows/query.yml')
    with f:
        #search_text = input('Please type a sentence: ')
        search_text = 'looked through every window then'
        doc = Document(content=search_text, mime_type='text/plain')
        f.post('/search', inputs=doc, on_done=print_result)


def query_restful():
    f = Flow.load_config("flows/query.yml")
    f.use_rest_gateway()
    with f:
        f.block()


@click.command()
@click.option('--task', '-t',
              type=click.Choice(['index', 'query', 'index_restful', 'query_restful', 'query_text'], case_sensitive=False))
@click.option('--num_docs', '-n', default=10000)
def main(task, num_docs):
    config()
    workspace = os.environ["JINA_WORKSPACE"]
    if task == 'index':
        if os.path.exists(workspace):
            logger.error(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
            sys.exit(1)
        index(num_docs)
    elif task == 'index_restful':
        index_restful(num_docs)
    elif task == 'query':
        query()
    elif task == 'query_text':
        query_text()
    elif task == 'query_restful':
        if not os.path.exists(workspace):
            logger.warning(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
        query_restful()
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
