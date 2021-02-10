__copyright__ = 'Copyright (c) 2021 Jina AI Limited. All rights reserved.'
__license__ = 'Apache-2.0'


import sys
import os

import click
from jina.flow import Flow

MAX_DOCS = int(os.environ.get('JINA_MAX_DOCS', 50))


def config():
    os.environ['JINA_DATA_FILE_1'] = os.environ.get(
        'JINA_DATA_FILE_1', 'data/input-1.txt'
    )
    os.environ['JINA_DATA_FILE_2'] = os.environ.get(
        'JINA_DATA_FILE_2', 'data/input-2.txt'
    )
    os.environ['JINA_WORKSPACE'] = os.environ.get('JINA_WORKSPACE', 'workspace')

    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def print_topk(resp, sentence):
    for d in resp.search.docs:
        print(f'Ta-Dah🔮, here are what we found for: {sentence}')
        for idx, match in enumerate(d.matches):

            score = match.score.value
            if score < 0.0:
                continue
            print(f'> {idx:>2d}({score:.2f}). {match.text}')


def index(num_docs):
    f = Flow().load_config('flows/index.yml')

    with f:
        print(f'Indexing {os.environ["JINA_DATA_FILE_1"]}')
        data_path = os.path.join(
            os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE_1', None)
        )
        f.index_lines(filepath=data_path, request_size=16, read_mode='r', size=num_docs)

    with f:
        print(f'Indexing {os.environ["JINA_DATA_FILE_2"]}')
        data_path = os.path.join(
            os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE_2', None)
        )
        f.index_lines(filepath=data_path, request_size=16, read_mode='r', size=num_docs)


def query(top_k):
    f = Flow().load_config('flows/query.yml')
    with f:
        while True:
            text = input('Please type a sentence: ')
            if not text:
                break

            def ppr(x):
                print_topk(x, text)

            f.search_lines(
                lines=[
                    text,
                ],
                line_format='text',
                on_done=ppr,
                top_k=top_k,
            )


def query_restful():
    f = Flow().load_config('flows/query.yml')
    f.use_rest_gateway()
    with f:
        f.block()


@click.command()
@click.option(
    '--task',
    '-t',
    type=click.Choice(['index', 'query', 'query_restful'], case_sensitive=False),
)
@click.option('--num_docs', '-n', default=MAX_DOCS)
@click.option('--top_k', '-k', default=5)
def main(task, num_docs, top_k):
    config()
    workspace = os.environ['JINA_WORKSPACE']
    if task == 'index':
        if os.path.exists(workspace):
            print(
                f'\n +----------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                         | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                         | \
                    \n +----------------------------------------------------------------------------------+'
            )
            sys.exit()
        index(num_docs)
    if task == 'query':
        if not os.path.exists(workspace):
            print(
                f'The directory {workspace} does not exist. Please index first via `python app.py -t index`'
            )
        query(top_k)
    if task == 'query_restful':
        if not os.path.exists(workspace):
            print(
                f'The directory {workspace} does not exist. Please index first via `python app.py -t index`'
            )
        query_restful()


if __name__ == '__main__':
    main()
