__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import random
import string

import click
from jina.flow import Flow

RANDOM_SEED = 14


def config():
    os.environ['PARALLEL'] = str(4)
    os.environ['SHARDS'] = str(2)
    os.environ['TMP_DATA_DIR'] = '/tmp/jina/audio_data/ESC-50-master'
    os.environ['JINA_PORT'] = str(45678)
    os.environ['WORKDIR'] = os.environ.get('WORKDIR', get_random_ws(os.environ['TMP_DATA_DIR']))


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
    data_path = os.path.join(os.environ['WORKDIR'], 'audio')
    if os.path.exists(data_path):
        print(f'\n +---------------------------------------------------------------------------------+ \
                \n |                                   🤖🤖🤖                                        | \
                \n | The directory {data_path} already exists. Please remove it before indexing again. | \
                \n |                                   🤖🤖🤖                                        | \
                \n +---------------------------------------------------------------------------------+')
    if task == 'index':
        f = Flow().load_config('./flows/flow-index.yml')
        with f:
            f.index_files(f'{data_path}/*.wav', size=num_docs, batch_size=2)
    elif task == 'query':
        f = Flow().load_config('./flows/flow-query.yml')
        f.use_rest_gateway()
        with f:
            f.block()
    elif task == 'dryrun':
        f = Flow.load_config('./flows/flow-query.yml')
        with f:
            pass
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query` or `dryrun`.')


if __name__ == '__main__':
    main()
