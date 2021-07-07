__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__version__ = '0.0.1'

import os
import sys
import click

from jina import Flow, Document
from helper import input_generator
from jina.logging.predefined import default_logger as logger


def config():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ.setdefault('JINA_WORKSPACE', os.path.join(cur_dir, 'workspace'))
    os.environ.setdefault('JINA_WORKSPACE_MOUNT',
                          f'{os.environ.get("JINA_WORKSPACE")}:/workspace/workspace')
    os.environ.setdefault('JINA_LOG_LEVEL', 'INFO')
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
        data_path = os.path.join(os.path.dirname(__file__),
                                 os.environ.get('JINA_DATA_FILE', None))
        flow.logger.info(f'Indexing {data_path}')
        flow.post(on='/index', inputs=input_docs, request_size=10,
                  show_progress=True)


# for search
def query():
    f = Flow.load_config('flows/query.yml')
    with f:
        f.block()


def query_text():
    def print_result(response):
        print(f'### Number of response documents: {len(response.docs)}')
        print(response.docs)
        # TODO Print matches here

    f = Flow.load_config('flows/query.yml')
    with f:
        search_text = input('Please type a sentence: ')
        doc = Document(content=search_text, mime_type='text/plain')
        response = f.post('/search', inputs=doc, return_results=True)
        print_result(response[0].data)


def query_restful():
    flow = Flow.load_config("flows/query.yml")
    flow.protocol = 'http'
    with flow:
        flow.block()


@click.command()
@click.option('--task', '-t',
              type=click.Choice(['index', 'query', 'query_restful', 'query_text'], case_sensitive=False))
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
            f'Unknown task: {task}.')


if __name__ == '__main__':
    main()
