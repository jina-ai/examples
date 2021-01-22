__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import click
import os
from jina.flow import Flow
from jina import Document

RANDOM_SEED = 14

cur_dir = os.path.dirname(os.path.abspath(__file__))


def config():
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', str(1))
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_SHARDS', str(1))
    os.environ['JINA_PORT'] = str(45678)
    os.environ['JINA_USES_VSE_IMAGE_ENCODER'] = os.environ.get('JINA_USES_VSE_IMAGE_ENCODER',
                                                               'docker://jinahub/pod.encoder.vseimageencoder:0.0.4-0.9.17')
    os.environ['JINA_USES_VSE_TEXT_ENCODER'] = os.environ.get('JINA_USES_VSE_TEXT_ENCODER',
                                                              'docker://jinahub/pod.encoder.vsetextencoder:0.0.3-0.9.17')


def input_index_data(num_docs=None, batch_size=8, dataset='f30k'):
    from dataset import get_data_loader
    captions = 'dataset_flickr30k.json' if dataset == 'f30k' else 'captions.txt'
    data_loader = get_data_loader(root=os.path.join(cur_dir, f'data/{dataset}/images'),
                                  captions=os.path.join(cur_dir, f'data/{dataset}/{captions}'),
                                  split='test',
                                  batch_size=batch_size,
                                  dataset_type=dataset)

    for i, (images, captions) in enumerate(data_loader):
        for image in images:
            with Document() as document:
                document.buffer = image
                document.modality = 'image'
                document.mime_type = 'image/jpeg'
            yield document

        for caption in captions:
            with Document() as document:
                document.text = caption
                document.modality = 'text'
                document.mime_type = 'text/plain'
            yield document

        if num_docs and (i + 1) * batch_size >= num_docs:
            break


def input_search_text_data(text):
    with Document() as document:
        document.text = text
        document.modality = 'text'
        document.mime_type = 'text/plain'
    return [document]


def input_search_image_file(image_file_path):
    with open(image_file_path, 'rb') as fp:
        image_buffer = fp.read()
    with Document() as document:
        document.buffer = image_buffer
        document.modality = 'image'
        document.mime_type = 'image/jpeg'
    return [document]


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
@click.option('--request_size', '-s', default=16)
@click.option('--data_set', '-d', type=click.Choice(['f30k', 'f8k'], case_sensitive=False), default='f8k')
def main(task, num_docs, request_size, data_set):
    config()
    if task == 'index':
        f = Flow().load_config('flow-index.yml')
        with f:
            f.index(input_fn=input_index_data(num_docs, request_size, data_set), request_size=request_size)
    elif task == 'query-restful':
        # not working, missing a way to send modality via REST API
        f = Flow().load_config('flow-query.yml')
        f.use_rest_gateway()
        with f:
            f.block()
    else:
        raise NotImplementedError(f'unknown task: {task}.'
                                  f' A valid task is either `index`, `query-restful`, `query-i2t` and `query-t2i`.')


if __name__ == '__main__':
    main()
