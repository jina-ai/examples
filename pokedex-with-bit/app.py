__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import click
import sys
from glob import glob

from jina import Flow, Document, Executor, requests
from jina.logging import default_logger as logger
from jina.logging.profile import TimeContext
from executors import *

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
    num_docs = min(num_docs, len(glob(os.path.join(os.getcwd(), IMAGE_SRC),
                                      recursive=True)))

    f = Flow(workspace="workspace")\
        .add(uses={"jtype": "ImageCrafter",
                   "with": {"target_size": 96,
                            "img_mean": [0.485, 0.456, 0.406],
                            "img_std": [0.229, 0.224, 0.225]}})
    f = f.add(uses=BigTransferEncoder)
    f = f.add(uses={"jtype": "EmbeddingIndexer",
                    "with": {"index_file_name": "image.json"},
                    "metas": {"name": "vec_idx"}},
              name="vec_idx")
    f = f.add(uses={"jtype": "KeyValueIndexer",
                    "metas": {"name": "doc_idx"}},
              name="kv_idx",
              needs="gateway")    # to enable parallel running
    f = f.add(name="join_all",
              needs=["kv_idx", "vec_idx"],
              read_only="true")

    with f:
        f.index(inputs=DocumentArray.from_files(IMAGE_SRC, size=num_docs),
                request_size=64, read_mode='rb')


def query_restful():
    f = Flow(workspace="workspace",
             port_expose=os.environ.get('JINA_PORT', str(45678)))\
        .add(uses={"jtype": "ImageCrafter",
                   "with": {"target_size": 96,
                            "img_mean": [0.485, 0.456, 0.406],
                            "img_std": [0.229, 0.224, 0.225]}})
    f = f.add(uses=BigTransferEncoder)
    f = f.add(uses={"jtype": "EmbeddingIndexer",
                    "with": {"index_file_name": "image.json"},
                    "metas": {"name": "vec_idx"}},
              name="vec_idx")
    f = f.add(uses={"jtype": "KeyValueIndexer",
                    "metas": {"name": "doc_idx"}},
              name="kv_idx")
    f = f.add(uses={"jtype": "MatchImageReader",
                    "with": {"target_size": 96,
                             "img_mean": [0.485, 0.456, 0.406],
                             "img_std": [0.229, 0.224, 0.225]}})
    f.use_rest_gateway()
    with f:
        f.block()


@click.command()
@click.option(
    '--task',
    '-t',
    type=click.Choice(
        ['index', 'query_restful'], case_sensitive=False
    ),
)
@click.option('--num_docs', '-n', default=MAX_DOCS)
def main(task: str, num_docs: int):
    config()
    workspace = os.environ['JINA_WORKSPACE']
    if task == 'index':
        if os.path.exists(workspace):
            logger.error(f'\n +----------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                         | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                         | \
                    \n +----------------------------------------------------------------------------------+')
            sys.exit(1)
        index(num_docs)
    if task == 'query_restful':
        if not os.path.exists(workspace):
            logger.error(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
            sys.exit(1)
        query_restful()


if __name__ == '__main__':
    main()