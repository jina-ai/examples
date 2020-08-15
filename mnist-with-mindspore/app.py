__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import click
import os
import string
import random
import numpy as np
from jina.flow import Flow


RANDOM_SEED = 14


def load_mnist(path):
    with open(path, 'rb') as fp:
        return np.frombuffer(fp.read(), dtype=np.uint8, offset=16).reshape([-1, 784])


def config():
    os.environ['PARALLEL'] = str(1)
    os.environ['SHARDS'] = str(1)
    os.environ['TMP_DATA_DIR'] = '/tmp/jina/mnist'
    os.environ['COLOR_CHANNEL_AXIS'] = str(0)
    os.environ['JINA_PORT'] = str(45678)
    os.environ['ENCODER'] = 'yaml/encode.yml'
    os.environ['TMP_WORKSPACE'] = os.environ.get('TMP_WORKSPACE', get_random_ws(os.environ['TMP_DATA_DIR']))


def get_random_ws(workspace_path, length=8):
    random.seed(RANDOM_SEED)
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
def main(task, num_docs):
    config()
    data_path = './MNIST_Data/test/t10k-images-idx3-ubyte'
    if task == 'index':
        f = Flow().load_config('mnist-index.yml')
        with f:
            f.index_ndarray(load_mnist(data_path), size=num_docs, batch_size=2)
    elif task == 'query':
        f = Flow().load_config('mnist-query.yml')
        f.use_rest_gateway()
        with f:
            f.block()
    else:
        raise NotImplementedError(f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
