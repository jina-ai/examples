__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import sys

import click
from jina.flow import Flow
from jina.logging import default_logger as logger


num_docs = os.environ.get('MAX_DOCS', 16)
data_path = 'data/**/*.jpg'
batch_size = 16

def clean_workdir():
    if os.path.exists(os.environ['WORKDIR']):
        shutil.rmtree(os.environ['WORKDIR'])
        logger.warning('Workspace deleted')


def config():
    parallel = 1 if sys.argv[1] == 'index' else 1
    shards = 1

    os.environ['PARALLEL'] = str(parallel)
    os.environ['SHARDS'] = str(shards)
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


@click.command()
@click.option('--task', '-task', type=click.Choice(['index', 'query'], case_sensitive=False))
@click.option('--return_image', '-r', default='original', type=click.Choice(['original', 'object'], case_sensitive=False))
@click.option('--data_path', '-p', default=data_path)
@click.option('--num_docs', '-n', default=num_docs)
@click.option('--batch_size', '-b', default=batch_size)
@click.option('--overwrite_workspace', '-overwrite', default=True)
def main(task, return_image, data_path, num_docs, batch_size, overwrite_workspace):
    config()
    if task == 'index':
        workspace = os.environ['WORKDIR']
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
        if overwrite_workspace:
            clean_workdir()
        f = Flow.load_config('flow-index.yml')
        with f:
            f.index_files(data_path, batch_size=batch_size, read_mode='rb', size=num_docs)        
    elif task == 'query':
        f = Flow.load_config(f'flow-query-{return_image}.yml')
        with f:
            f.block()

if __name__ == '__main__':
    main()
