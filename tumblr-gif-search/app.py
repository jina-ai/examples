__copyright__ = "Copyright (c) 2020 - 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
from glob import glob

import click
from jina.flow import Flow

GIF_BLOB = 'data/*.gif'
# TODO test w 2
SHARDS_DOC = 2
SHARDS_CHUNK_SEG = 2
SHARDS_INDEXER = 2
JINA_TOPK = 11
MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 50))


def config():
    os.environ['SHARDS_DOC'] = str(SHARDS_DOC)
    os.environ['JINA_TOPK'] = str(JINA_TOPK)
    os.environ['SHARDS_CHUNK_SEG'] = str(SHARDS_CHUNK_SEG)
    os.environ['SHARDS_INDEXER'] = str(SHARDS_INDEXER)
    os.environ['JINA_WORKSPACE'] = './workspace'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def index(num_docs: int):
    f = Flow.load_config('flow-index.yml')

    with f:
        f.index_files(GIF_BLOB, request_size=10, read_mode='rb', skip_dry_run=True, size=num_docs)


def query_restful():
    f = Flow.load_config('flow-query.yml')
    f.use_rest_gateway()

    with f:
        f.block()


def dryrun():
    f = Flow.load_config('flow-query.yml')
    with f:
        pass


@click.command()
@click.option(
    "--task",
    "-t",
    type=click.Choice(
        ["index", "query"], case_sensitive=False
    ),
)
@click.option("--num-docs", "-n", default=MAX_DOCS)
def main(task: str, num_docs: int):
    config()
    workspace = os.environ['JINA_WORKSPACE']

    if task == "index":
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                       \n |                                   🤖🤖🤖                                        | \
                       \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                       \n |                                   🤖🤖🤖                                        | \
                       \n +---------------------------------------------------------------------------------+')
            sys.exit(1)
        index(num_docs)
    if task == "query":
        if not os.path.exists(workspace):
            print(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
        query()
    if task == "dryrun":
        dryrun()


if __name__ == '__main__':
    main()
