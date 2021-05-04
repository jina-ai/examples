__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

import click
import requests
from jina import Document
from jina.clients.sugary_io import _input_lines
from jina import Flow

from dataset import input_index_data


cur_dir = os.path.dirname(os.path.abspath(__file__))


def config(model_name):
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '1')
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_SHARDS', '1')
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")
    os.environ['JINA_PORT'] = '45678'
    os.environ['JINA_USE_REST_API'] = 'true'
    if model_name == 'clip':
        os.environ['JINA_IMAGE_ENCODER'] = os.environ.get('JINA_IMAGE_ENCODER', 'docker://jinahub/pod.encoder.clipimageencoder:0.0.2-1.1.0')
        os.environ['JINA_TEXT_ENCODER'] = os.environ.get('JINA_TEXT_ENCODER', 'docker://jinahub/pod.encoder.cliptextencoder:0.0.2-1.1.0')
        os.environ['JINA_TEXT_ENCODER_INTERNAL'] = 'yaml/clip/text-encoder.yml'
    elif model_name == 'vse':
        os.environ['JINA_IMAGE_ENCODER'] = os.environ.get('JINA_IMAGE_ENCODER', 'docker://jinahub/pod.encoder.vseimageencoder:0.0.5-1.0.7')
        os.environ['JINA_TEXT_ENCODER'] = os.environ.get('JINA_TEXT_ENCODER', 'docker://jinahub/pod.encoder.vsetextencoder:0.0.6-1.0.7')
        os.environ['JINA_TEXT_ENCODER_INTERNAL'] = 'yaml/vse/text-encoder.yml'


def index_restful(num_docs):
    f = Flow().load_config('flow-index.yml')

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
    f = Flow().load_config('flow-query.yml')
    f.use_rest_gateway()
    with f:
        f.block()

def dryrun():
    f = Flow().load_config('flow-index.yml')
    with f:
        pass


@click.command()
@click.option('--task', '-t', type=click.Choice(['index', 'index_restful', 'query', 'query_restful', 'dryrun'], case_sensitive=False), default='query')
@click.option('--num_docs', '-n', default=50)
@click.option('--request_size', '-s', default=16)
@click.option('--data_set', '-d', type=click.Choice(['f30k', 'f8k'], case_sensitive=False), default='f8k')
@click.option('--model_name', '-m', type=click.Choice(['clip', 'vse'], case_sensitive=False), default='clip')
def main(task, num_docs, request_size, data_set, model_name):
    config(model_name)
    workspace = os.environ['JINA_WORKSPACE']
    if 'index' in task:
        if os.path.exists(workspace):
            print(
                f'\n +------------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                           | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                           | \
                    \n +------------------------------------------------------------------------------------+'
            )
            sys.exit(1)

    print(f'### task = {task}')
    if task == 'index':
        with Flow.load_config('flow-index.yml') as f:
            f.index(
                input_fn=input_index_data(num_docs, request_size, data_set),
                request_size=request_size
            )
    elif task == 'index_restful':
        index_restful(num_docs)
    elif task == 'query':
        with Flow.load_config('flow-query.yml') as f:
            f.use_rest_gateway()
            f.block()
    elif task == 'query_restful':
        if not os.path.exists(workspace):
            print(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
        query_restful()
    elif task == 'dryrun':
        dryrun()

if __name__ == '__main__':
    main()
