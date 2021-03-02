__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os

import click

from jina import Flow
from jina import Document

cur_dir = os.path.dirname(os.path.abspath(__file__))

def config():
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '1')
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_SHARDS', '1')
    os.environ['JINA_PORT'] = '45678'


def input_index_data(num_docs=None, batch_size=8, dataset_type='f30k'):
    from dataset import get_data_loader
    captions = 'dataset_flickr30k.json' if dataset_type == 'f30k' else 'captions.txt'
    data_loader = get_data_loader(
        root=os.path.join(cur_dir, f'data/{dataset_type}/images'),
        captions=os.path.join(cur_dir, f'data/{dataset_type}/{captions}'),
        split='test',
        batch_size=batch_size,
        dataset_type=dataset_type
    )

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


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
@click.option('--request_size', '-s', default=16)
@click.option('--data_set', '-d', type=click.Choice(['f30k', 'f8k'], case_sensitive=False), default='f8k')
def main(task, num_docs, request_size, data_set):
    config()
    if task == 'index':
        with Flow().load_config('flow-index.yml') as f:
            f.index(
                input_fn=input_index_data(num_docs, request_size, data_set),
                request_size=request_size
            )
    elif task == 'query-restful':
        with Flow().load_config('flow-query.yml') as f:
            f.use_rest_gateway()
            f.block()
    else:
        msg = f'Unknown task {task}'
        msg += 'A valid task is either `index` or `query-restful`.'
        raise Exception(msg)


if __name__ == '__main__':
    main()
