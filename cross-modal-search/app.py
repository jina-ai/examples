__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import click
import os
from jina.flow import Flow

RANDOM_SEED = 14

cur_dir = os.path.dirname(os.path.abspath(__file__))


def config():
    os.environ['PARALLEL'] = str(1)
    os.environ['SHARDS'] = str(1)
    os.environ['COLOR_CHANNEL_AXIS'] = str(0)
    os.environ['JINA_PORT'] = str(45678)
    os.environ['JINA_PORT'] = ''


def input_index_data(num_docs=None, batch_size=8):
    from jina.proto import jina_pb2
    from dataset import get_data_loader
    data_loader = get_data_loader(root=os.path.join(cur_dir, 'data/f30k/images'),
                                  json=os.path.join(cur_dir, 'data/f30k/dataset_flickr30k.json'),
                                  split='test',
                                  batch_size=batch_size)
    for i, (images, captions) in enumerate(data_loader):
        for image in images:
            document = jina_pb2.Document()
            document.buffer = image
            document.modality = 'image'
            yield document

        for caption in captions:
            document = jina_pb2.Document()
            document.text = caption
            document.modality = 'text'
            yield document

        if num_docs and (i + 1) * batch_size >= num_docs:
            break


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
@click.option('--batch_size', '-b', default=16)
def main(task, num_docs, batch_size):
    config()
    if task == 'index':
        f = Flow().load_config('flow-index.yml')
        with f:
            f.index(input_index_data(num_docs, batch_size), batch_size=batch_size)
    else:
        raise NotImplementedError(f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()

