__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

import click
from jina.flow import Flow
from jina.logging import JinaLogger
from jina.logging.profile import TimeContext
from jina.logging import default_logger as logger

logger = JinaLogger('wikipedia-example')


MAX_DOCS = int(os.environ.get('JINA_MAX_DOCS', 50))


def config():
    os.environ['JINA_DATA_FILE'] = os.environ.get('JINA_DATA_FILE', 'data/toy-input.txt')
    os.environ['JINA_DATA_FILE_INC'] = os.environ.get('JINA_DATA_FILE_INC', 'data/toy-input-incremental.txt')
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


def _index(f, data_fn, num_docs):
    with f:
        f.logger.info(f'Indexing {os.environ[data_fn]}')
        data_path = os.path.join(os.path.dirname(__file__), os.environ.get(data_fn, None))
        num_docs = min(num_docs, len(open(data_path).readlines()))
        with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
            f.index_lines(filepath=data_path, batch_size=16, read_mode='r', size=num_docs)


def index(num_docs):
    f = Flow().load_config('flows/index.yml')
    _index(f, 'JINA_DATA_FILE', num_docs)


def index_incremental(num_docs):
    f = Flow().load_config('flows/index_incremental.yml')
    for data_fn in ('JINA_DATA_FILE', 'JINA_DATA_FILE_INC'):
        _index(f, data_fn, num_docs)


def query(top_k):
    def ppr(x):
        print_topk(x, text)

    f = Flow().load_config('flows/query.yml')
    with f:
        while True:
            text = input('please type a sentence: ')
            if not text:
                break
            f.search_lines(
                lines=[
                    text,
                ],
                line_format='text',
                on_done=ppr,
                top_k=top_k
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
    type=click.Choice(['index', 'index_incremental', 'query', 'query_restful'], case_sensitive=False),
)
@click.option('--num_docs', '-n', default=MAX_DOCS)
@click.option('--top_k', '-k', default=5)
def main(task, num_docs, top_k):
    config()
    workspace = os.environ['JINA_WORKSPACE']
    if 'index' in task:
        if os.path.exists(workspace):
            logger.error(
                f'\n +------------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                           | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                           | \
                    \n +------------------------------------------------------------------------------------+'
            )
            sys.exit(1)
    if 'query' in task:
        if not os.path.exists(workspace):
            print(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
            sys.exit(1)
    if task == 'index':
        index(num_docs)
    elif task == 'index_incremental':
        index_incremental(num_docs)
    elif task == 'query':
        query(top_k)
    elif task == 'query_restful':
        query_restful()


if __name__ == '__main__':
    main()
