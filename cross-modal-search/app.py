__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

import click
from jina import Flow
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
    os.environ['JINA_IMAGE_ENCODER'] = os.environ.get('JINA_IMAGE_ENCODER', 'docker://jinahub/pod.encoder.clipimageencoder:0.0.2-1.2.0')
    os.environ['JINA_TEXT_ENCODER'] = os.environ.get('JINA_TEXT_ENCODER', 'docker://jinahub/pod.encoder.cliptextencoder:0.0.3-1.2.2')
    os.environ['JINA_TEXT_ENCODER_INTERNAL'] = 'pods/clip/text-encoder.yml'

def index_restful(num_docs):
    flow = Flow().load_config('flows/flow-index.yml')

    with flow:
        data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None))
        flow.logger.info(f'Indexing {data_path}')
        url = f'http://0.0.0.0:{flow.port_expose}/index'

        input_docs = _input_lines(
            filepath=data_path,
            size=num_docs,
            read_mode='r',
        )
        data_json = {'data': [Document(text=text).dict() for text in input_docs]}
        r = requests.post(url, json=data_json)
        if r.status_code != 200:
            raise Exception(f'api request failed, url: {url}, status: {r.status_code}, content: {r.content}')


def index(data_set, num_docs, request_size):
    flow = Flow.load_config('flows/flow-index.yml')
    flow.plot()
    with flow:
        with TimeContext(f'QPS: indexing {num_docs}', logger=flow.logger):
            flow.index(
                inputs=input_index_data(num_docs, request_size, data_set),
                request_size=request_size
            )


def query_restful():
    flow = Flow().load_config('flows/flow-query.yml')
    flow.use_rest_gateway()
    with flow:
        flow.block()


def dryrun():
    flow = Flow().load_config('flows/flow-index.yml')
    with flow:
        pass


@click.command()
@click.option('--task', '-t', type=click.Choice(['index', 'index_restful', 'query_restful', 'dryrun'], case_sensitive=False), default='index')
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
        index_restful(num_docs)
    elif task == 'query_restful':
        query_restful()
    elif task == 'dryrun':
        dryrun()


if __name__ == '__main__':
    main()
