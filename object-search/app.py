__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import sys
from glob import glob

import click
from jina.flow import Flow
from jina.logging import default_logger as logger
from jina.logging.profile import TimeContext

MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 50))
IMAGE_SRC = 'data/**/*.jpg'


def config():
    os.environ["JINA_DATA_FILE"] = os.environ.get("JINA_DATA_FILE", "data/toy-data")
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")
    os.environ['PARALLEL'] = str(1)
    os.environ['SHARDS'] = str(1)
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))
    os.environ['WORKDIR'] = './workspace'


def index(num_docs: int):
    f = Flow.load_config('flow-index.yml')
    num_docs = min(num_docs, len(glob(IMAGE_SRC)))
    with f:
        with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
            f.index_files(IMAGE_SRC, request_size=10, read_mode='rb', size=num_docs)


def query(return_image: str):
    f = Flow.load_config(f'flow-query-{return_image}.yml')
    f.use_rest_gateway()

    # no perf measure, as it opens a REST api and blocks
    with f:
        f.block()


# for test before put into docker
def dryrun():
    f = Flow().load_config('flow-index.yml')
    with f:
        pass


@click.command()
@click.option('--task', '-t', type=click.Choice(['index', 'query', 'dry'], case_sensitive=False))
@click.option('--return_image', '-r', default='original', type=click.Choice(['original', 'object'], case_sensitive=False))
@click.option('--num_docs', '-n', default=MAX_DOCS)
def main(task: str, return_image: str, num_docs: int):
    config()
    workspace = os.environ['WORKDIR']
    if task == 'index':
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
            sys.exit(1)
        index(num_docs)
    if task == 'query':
        if not os.path.exists(workspace):
            print(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
            sys.exit(1)
        query(return_image)


if __name__ == '__main__':
    main()
