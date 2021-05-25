__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

import copy
import click
import shutil
import numpy as np
from jina import Flow, Document, DocumentArray
from jina.logging.profile import TimeContext


from transformer import MyTransformer
from indexer import NumpyIndexer

MAX_DOCS = int(os.environ.get('JINA_MAX_DOCS', 50))

def config():
    os.environ['JINA_DATA_FILE'] = os.environ.get('JINA_DATA_FILE', 'data/input.txt')
    os.environ['JINA_WORKSPACE'] = os.environ.get('JINA_WORKSPACE', 'workspace')
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def print_topk(resp, sentence):
    for doc in resp.data.docs:
        print(f"Ta-Dah🔮, here's what we found for: {sentence}")
        for idx, match in enumerate(doc.matches):

            score = match.score.value
            if score < 0.0:
                continue
            print(f'> {idx:>2d}({score:.2f}). {match.text}')

def index(num_docs):
    f = Flow().add(uses=MyTransformer).add(uses=NumpyIndexer)
    data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None))
    assert(os.environ.get('JINA_DATA_FILE', None)=='data/input.txt')
    with f, open(data_path) as fp:
        docs = DocumentArray.from_ndarray(np.array(fp.readlines()))
        num_docs = min(num_docs, len(fp.readlines()))
        with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
            f.index(docs)

            text = input('Please type a sentence: ')

            doc = Document(content=text)

            def ppr(x):
                print_topk(x, text)

            f.search(doc,
                     parameters={'top_k': 1},
                     line_format='text',
                     on_done=ppr,
                     )

def query(top_k):
    f = Flow(restful=True).add(uses=MyTransformer).add(uses=NumpyIndexer)
    with f:
        while True:
            text = input('Please type a sentence: ')
            if not text:
                break

            doc = Document(content=text)

            def ppr(x):
                print_topk(x, text)

            f.search(doc,
                parameters={},
                line_format='text',
                on_done=ppr,
                top_k=top_k,
            )


def query_restful(return_flow=False):
    f = Flow().load_config('flows/query.yml')
    f.use_rest_gateway()
    if return_flow:
        return f
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

    shutil.rmtree('workspace', ignore_errors=True)
    os.makedirs('workspace')
    '''
    if 'index' in task:
        if os.path.exists(workspace):
            logger.error(
                f'\n +------------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                           | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                           | \
                    \n +------------------------------------------------------------------------------------+'
            )
            sys.exit(1)'''
    if 'query' in task:
        if not os.path.exists(workspace):
            print(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
            sys.exit(1)
    if task == 'index':
        index(num_docs)
    elif task == 'query':
        query(top_k)
    elif task == 'query_restful':
        query_restful()



if __name__ == '__main__':
    main()
