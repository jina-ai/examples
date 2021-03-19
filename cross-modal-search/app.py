__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os

import click
from jina import Flow

from dataset import input_index_data


cur_dir = os.path.dirname(os.path.abspath(__file__))


def config(model_name):
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '1')
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_SHARDS', '1')
    os.environ['JINA_PORT'] = '45678'
    os.environ['JINA_USE_REST_API'] = 'true'
    if model_name == 'clip':
        os.environ['JINA_IMAGE_ENCODER'] = os.environ.get('JINA_IMAGE_ENCODER', 'docker://jinahub/pod.encoder.clipimageencoder:0.0.1-1.0.7')
        os.environ['JINA_TEXT_ENCODER'] = os.environ.get('JINA_TEXT_ENCODER', 'docker://jinahub/pod.encoder.cliptextencoder:0.0.1-1.0.7')
        os.environ['JINA_TEXT_ENCODER_INTERNAL'] = 'yaml/clip/text-encoder.yml'
    elif model_name == 'vse':
        os.environ['JINA_IMAGE_ENCODER'] = os.environ.get('JINA_IMAGE_ENCODER', 'docker://jinahub/pod.encoder.vseimageencoder:0.0.5-1.0.7')
        os.environ['JINA_TEXT_ENCODER'] = os.environ.get('JINA_TEXT_ENCODER', 'docker://jinahub/pod.encoder.vsetextencoder:0.0.6-1.0.7')
        os.environ['JINA_TEXT_ENCODER_INTERNAL'] = 'yaml/vse/text-encoder.yml'


@click.command()
@click.option('--task', '-t', type=click.Choice(['index', 'query'], case_sensitive=False), default='query')
@click.option('--num_docs', '-n', default=50)
@click.option('--request_size', '-s', default=16)
@click.option('--data_set', '-d', type=click.Choice(['f30k', 'f8k'], case_sensitive=False), default='f8k')
@click.option('--model_name', '-m', type=click.Choice(['clip', 'vse'], case_sensitive=False), default='clip')
def main(task, num_docs, request_size, data_set, model_name):
    config(model_name)
    if task == 'index':
        with Flow.load_config('flow-index.yml') as f:
            f.index(
                input_fn=input_index_data(num_docs, request_size, data_set),
                request_size=request_size
            )
    elif task == 'query':
        with Flow.load_config('flow-query.yml') as f:
            f.use_rest_gateway()
            f.block()


if __name__ == '__main__':
    main()
