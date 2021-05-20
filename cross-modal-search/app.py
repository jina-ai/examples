__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

import click
from jina import Flow
from jina.logging import JinaLogger
from jina.logging.profile import TimeContext

from dataset import input_index_data

MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 50))
cur_dir = os.path.dirname(os.path.abspath(__file__))


def config(model_name):
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '1')
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_SHARDS', '1')
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")
    os.environ['JINA_PORT'] = '45678'
    if model_name == 'clip':
        os.environ['JINA_IMAGE_ENCODER'] = os.environ.get('JINA_IMAGE_ENCODER', 'docker://jinahub/pod.encoder.clipimageencoder:0.0.2-1.2.0')
        os.environ['JINA_TEXT_ENCODER'] = os.environ.get('JINA_TEXT_ENCODER', 'docker://jinahub/pod.encoder.cliptextencoder:0.0.3-1.2.2')
        os.environ['JINA_TEXT_ENCODER_INTERNAL'] = 'yaml/clip/text-encoder.yml'
    elif model_name == 'vse':
        os.environ['JINA_IMAGE_ENCODER'] = os.environ.get('JINA_IMAGE_ENCODER', 'docker://jinahub/pod.encoder.vseimageencoder:0.0.5-1.2.0')
        os.environ['JINA_TEXT_ENCODER'] = os.environ.get('JINA_TEXT_ENCODER', 'docker://jinahub/pod.encoder.vsetextencoder:0.0.6-1.2.0')
        os.environ['JINA_TEXT_ENCODER_INTERNAL'] = 'yaml/vse/text-encoder.yml'


def index(data_set, num_docs, request_size):
    f = Flow.load_config('flow-index.yml')
    with f:
        with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
            f.index(
                inputs=input_index_data(num_docs, request_size, data_set),
                request_size=request_size
            )


def query_restful():
    f = Flow.load_config('flow-query.yml')
    f.use_rest_gateway()
    with f:
        f.block()


@click.command()
@click.option('--task',
              '-t',
              type=click.Choice(['index', 'query_restful'], case_sensitive=False),
              default='query_restful')
@click.option("--num_docs", "-n", default=MAX_DOCS)
@click.option('--request_size', '-s', default=12)
@click.option('--data_set', '-d', type=click.Choice(['f30k', 'f8k'], case_sensitive=False), default='f8k')
@click.option('--model_name', '-m', type=click.Choice(['clip', 'vse'], case_sensitive=False), default='clip')
def main(task, num_docs, request_size, data_set, model_name):
    config(model_name)
    workspace = os.environ['JINA_WORKSPACE']
    logger = JinaLogger('cross-modal-search')
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
    if 'query' in task and not os.path.exists(workspace):
        logger.info(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
        sys.exit(1)
    logger.info(f'### task = {task}')
    if task == 'index':
        index(data_set, num_docs, request_size)
    if task == 'query_restful':
        query_restful()


if __name__ == '__main__':
    main()
