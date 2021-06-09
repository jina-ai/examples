__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import shutil
import click
import sys
from glob import glob

from jina import Flow, DocumentArray
from jina.types.document.generators import from_files
from jina.logging import default_logger as logger
from executors import *

MAX_DOCS = int(os.environ.get('JINA_MAX_DOCS', 50000))
IMAGE_SRC = 'data/**/*.png'

os.environ['JINA_WORKSPACE'] = './workspace'
os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def index(num_docs: int):
    num_docs = min(num_docs, len(glob(os.path.join(os.getcwd(), IMAGE_SRC),
                                      recursive=True)))

    flow = Flow(workspace="workspace")\
        .add(uses={"jtype": "ImageCrafter",
                   "with": {"target_size": 96,
                            "img_mean": [0.485, 0.456, 0.406],
                            "img_std": [0.229, 0.224, 0.225]}}) \
        .add(uses=BigTransferEncoder) \
        .add(uses={"jtype": "EmbeddingIndexer",
                   "with": {"index_file_name": "image.json"},
                   "metas": {"name": "vec_idx"}},
             name="vec_idx") \
        .add(uses={"jtype": "KeyValueIndexer",
                   "metas": {"name": "kv_idx"}},
             name="kv_idx",
             needs="gateway") \
        .add(name="join_all",
             needs=["kv_idx", "vec_idx"],
             read_only="true")

    with flow:
        document_generator = from_files(IMAGE_SRC, size=num_docs)
        flow.post(on='/index', inputs=DocumentArray(document_generator),
                  request_size=64, read_mode='rb')


def query_restful():
    flow = Flow(workspace="workspace",
                port_expose=os.environ.get('JINA_PORT', str(45678)))\
        .add(uses={"jtype": "ImageCrafter",
                   "with": {"target_size": 96,
                            "img_mean": [0.485, 0.456, 0.406],
                            "img_std": [0.229, 0.224, 0.225]}})\
        .add(uses=BigTransferEncoder)\
        .add(uses={"jtype": "EmbeddingIndexer",
                   "with": {"index_file_name": "image.json"},
                   "metas": {"name": "vec_idx"}},
             name="vec_idx")\
        .add(uses={"jtype": "KeyValueIndexer",
                   "metas": {"name": "kv_idx"}},
             name="kv_idx")\
        .add(uses={"jtype": "MatchImageReader"})
    flow.use_rest_gateway()
    with flow:
        flow.block()


@click.command()
@click.option(
    '--task',
    '-t',
    type=click.Choice(
        ['index', 'query_restful'], case_sensitive=False
    ),
)
@click.option('--num_docs', '-n', default=MAX_DOCS)
@click.option('--force', '-f', is_flag=True)
def main(task: str, num_docs: int, force: bool):
    workspace = os.environ['JINA_WORKSPACE']
    if task == 'index':
        if os.path.exists(workspace):
            if force:
                shutil.rmtree(workspace)
            else:
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
