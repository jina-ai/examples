__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__copyright__ = 'Copyright (c) 2020 Jina AI Limited. All rights reserved.'
__license__ = 'Apache-2.0'

import os

import click
from jina.flow import Flow


def config():
    os.environ['JINA_DATA_FILE_1'] = os.environ.get(
        'JINA_DATA_FILE_1', 'data/character-lines-1.csv'
    )
    os.environ['JINA_DATA_FILE_2'] = os.environ.get(
        'JINA_DATA_FILE_2', 'data/character-lines-2.csv'
    )
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_SHARDS', '2')
    os.environ['JINA_WORKSPACE'] = os.environ.get('JINA_WORKSPACE', 'workspace')

    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def print_topk(resp, sentence):
    for d in resp.search.docs:
        print(f'Ta-Dah🔮, here are what we found for: {sentence}')
        for idx, match in enumerate(d.matches):

            score = match.score.value
            if score < 0.0:
                continue
            character = match.meta_info.decode()
            dialog = match.text.strip()
            print(f'> {idx:>2d}({score:.2f}). {character.upper()} said, "{dialog}"')


def index(num_docs):
    f = Flow().load_config('flow-index.yml')

    with f:
        print(f'Indexing file {os.environ["JINA_DATA_FILE_1"]}')
        f.index_lines(
            filepath=os.environ['JINA_DATA_FILE_1'],
            batch_size=8,
            size=num_docs,
        )

    # we then re-use the same index to append new data
    with f:
        print(f'Indexing file {os.environ["JINA_DATA_FILE_2"]}')
        f.index_lines(
            filepath=os.environ['JINA_DATA_FILE_2'],
            batch_size=8,
            size=num_docs,
        )


def query(top_k):
    f = Flow().load_config('flow-query.yml')
    with f:
        while True:
            text = input('please type a sentence: ')
            if not text:
                break

            def ppr(x):
                print_topk(x, text)

            f.search_lines(
                lines=[
                    text,
                ],
                output_fn=ppr,
                top_k=top_k,
            )


def query_restful():
    f = Flow().load_config('flow-query.yml')
    f.use_rest_gateway()
    with f:
        f.block()


@click.command()
@click.option(
    '--task',
    '-t',
    type=click.Choice(['index', 'query', 'query_restful'], case_sensitive=False),
)
@click.option('--num_docs', '-n', default=50)
@click.option('--top_k', '-k', default=5)
def main(task, num_docs, top_k):
    config()
    workspace = os.environ['JINA_WORKSPACE']
    if task == 'index':
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
