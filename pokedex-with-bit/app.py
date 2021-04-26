__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
from glob import glob

import click
from jina.flow import Flow
from jina.logging.profile import TimeContext

MAX_DOCS = int(os.environ.get('JINA_MAX_DOCS', 50000))
IMAGE_SRC = 'data/**/*.png'


def config():
    num_encoders = 1 if sys.argv[1] == 'index' else 1
    shards = 8

    os.environ['JINA_SHARDS'] = str(num_encoders)
    os.environ['JINA_SHARDS_INDEXERS'] = str(shards)
    os.environ['JINA_WORKSPACE'] = './workspace'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def index(num_docs: int):
    f = Flow.load_config('flows/index.yml')
    num_docs = min(num_docs, len(glob(os.path.join(os.getcwd(), IMAGE_SRC), recursive=True)))

    with f:
        with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
            f.index_files(IMAGE_SRC, request_size=64, read_mode='rb', size=num_docs)


def query():
    f = Flow.load_config('flows/query.yml')
    f.use_rest_gateway()

    # no perf measure, as it opens a REST api and blocks
    with f:
        f.block()


@click.command()
@click.option(
    "--task",
    "-t",
    type=click.Choice(
        ["index", "query"], case_sensitive=False
    ),
)
@click.option("--num_docs", "-n", default=MAX_DOCS)
def main(task: str, num_docs: int):
    config()
    workspace = os.environ["JINA_WORKSPACE"]
    if task == "index":
        if os.path.exists(workspace):
            print(f'\n +----------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                         | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                         | \
                    \n +----------------------------------------------------------------------------------+')
            sys.exit(1)
        index(num_docs)
    if task == "query":
        if not os.path.exists(workspace):
            print(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
            sys.exit(1)
        query()


if __name__ == '__main__':
    main()
