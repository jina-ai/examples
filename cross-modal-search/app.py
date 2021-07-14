__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

import click
from jina import Flow, Document
import logging
from jina.logging.profile import TimeContext

from dataset import input_index_data

MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 50))
cur_dir = os.path.dirname(os.path.abspath(__file__))


def config():
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '1')
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_SHARDS', '1')
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")
    os.environ['JINA_PORT'] = '45678'


def index_restful():
    flow = Flow().load_config('flows/flow-index.yml', override_with={'protocol': 'http'})
    with flow:
        flow.block()


def check_index_result(resp):
    for doc in resp.data.docs:
        _doc = Document(doc)
        print(f'{_doc.id[:10]}, buffer: {len(_doc.buffer)}, mime_type: {_doc.mime_type}, modality: {_doc.modality}, embed: {_doc.embedding.shape}, uri: {_doc.uri[:20]}')


def check_query_result(resp):
    for doc in resp.data.docs:
        _doc = Document(doc)
        print(f'{_doc.id[:10]}, buffer: {len(_doc.buffer)}, embed: {_doc.embedding.shape}, uri: {_doc.uri[:20]}, chunks: {len(_doc.chunks)}, matches: {len(_doc.matches)}')
        if _doc.matches:
            for m in _doc.matches:
                print(f'\t+- {m.id[:10]}, score: {m.scores["doc_score"].value}, text: {m.text}, modality: {m.modality}, uri: {m.uri[:20]}')


def index(data_set, num_docs, request_size):
    flow = Flow().load_config('flows/flow-index.yml')
    with flow:
        with TimeContext(f'QPS: indexing {num_docs}', logger=flow.logger):
            flow.index(
                inputs=input_index_data(num_docs, request_size, data_set),
                request_size=request_size,
                on_done=check_index_result
            )


def query():
    flow = Flow().load_config('flows/flow-query.yml')
    with flow:
        flow.search(inputs=[
            Document(text='a black dog and a spotted dog are fighting', modality='text'),
            Document(uri='toy-data/images/1000268201_693b08cb0e.jpg', modality='image')
        ],
            on_done=check_query_result)


def query_restful():
    flow = Flow().load_config('flows/flow-query.yml', override_with={'protocol': 'http'})
    with flow:
        flow.block()


@click.command()
@click.option('--task', '-t', type=click.Choice(['index', 'index_restful', 'query_restful', 'query']), default='index')
@click.option("--num_docs", "-n", default=MAX_DOCS)
@click.option('--request_size', '-s', default=16)
@click.option('--data_set', '-d', type=click.Choice(['f30k', 'f8k', 'toy-data'], case_sensitive=False), default='toy-data')
def main(task, num_docs, request_size, data_set):
    config()
    workspace = os.environ['JINA_WORKSPACE']
    logger = logging.getLogger('cross-modal-search')
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
            logger.error(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
            sys.exit(1)

    if task == 'index':
        index(data_set, num_docs, request_size)
    elif task == 'index_restful':
        index_restful()
    elif task == 'query':
        query()
    elif task == 'query_restful':
        query_restful()


if __name__ == '__main__':
    main()
