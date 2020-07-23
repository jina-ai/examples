__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import click
import os
import string
import random
import sys
import io
from PIL import Image
from jina.flow import Flow

RANDOM_SEED = 14
os.environ['PARALLEL'] = str(1)
os.environ['SHARDS'] = str(1)
os.environ['TMP_DATA_DIR'] = '/tmp/jina/flower'
os.environ['COLOR_CHANNEL_AXIS'] = str(0)
os.environ['JINA_PORT'] = str(45678)
os.environ['ENCODER'] = os.environ.get('ENCODER', 'jinaai/hub.executors.encoders.image.torchvision-mobilenet_v2')


def get_random_ws(workspace_path, length=8):
    random.seed(RANDOM_SEED)
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
def main(task, num_docs):
    os.environ['TMP_WORKSPACE'] = os.environ.get('TMP_WORKSPACE', get_random_ws(os.environ['TMP_DATA_DIR']))
    data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'jpg')
    if task == 'index':
        f = Flow().load_config('flow-index.yml')
        with f:
            f.index_files(f'{data_path}/*.jpg', size=num_docs, read_mode='rb', batch_size=2)
    elif task == 'query':
        f = Flow().load_config('flow-query.yml')
        f.use_rest_gateway()
        with f:
            f.block()
    else:
        raise NotImplementedError(f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()

