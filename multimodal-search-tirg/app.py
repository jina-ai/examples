__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import sys

import click
from jina.flow import Flow
from jina.logging import default_logger as logger


num_docs = 8
data_path = 'data/*/*.jpeg'
batch_size = 8

def clean_workdir():
    if os.path.exists(os.environ['WORKDIR']):
        shutil.rmtree(os.environ['WORKDIR'])
        logger.warning('Workspace deleted')


def config():
    os.environ['PARALLEL'] = '1'
    os.environ['SHARDS'] = '1'
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = '45678'


@click.command()
@click.option('--task', '-task', type=click.Choice(['index', 'query'], case_sensitive=False))
@click.option('--data_path', '-p', default=data_path)
@click.option('--num_docs', '-n', default=num_docs)
@click.option('--batch_size', '-b', default=batch_size)
@click.option('--overwrite_workspace', '-overwrite', default=True)
def main(task, data_path, num_docs, batch_size, overwrite_workspace):
    config()
    if task == 'index':
        if overwrite_workspace:
            clean_workdir()
        f = Flow.load_config('flow-index.yml')
        with f:
            f.index_files(data_path, batch_size=batch_size, read_mode='rb', size=num_docs)        
    elif task == 'query':
        f = Flow.load_config('flow-query.yml')
        with f:
            f.block()

if __name__ == '__main__':
    main()
