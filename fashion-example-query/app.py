__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

import click
from collections import defaultdict

import random

from jina import Document, Flow
from jina.logging.profile import TimeContext
from jina.logging import JinaLogger
from jina.helloworld.helper import download_data, write_html, print_result

from pkg_resources import resource_filename

result_html = []
TOP_K = 10
num_docs_evaluated = 0
evaluation_value = defaultdict(float)

label_id = {
    0: 'T-shirt/top',
    1: 'Trouser',
    2: 'Pullover'
}


def get_mapped_label(label_int: str):
    """
    Get a label_int and return the description of that label
    label_int   Description
    0           T-shirt/top
    1           Trouser
    2           Pullover
    """
    return label_id.get(label_int, "Invalid tag")


def download_fashionmnist():
    target_tuple = [
        ('index-labels', 'train-labels-idx1-ubyte.gz'),
        ('query-labels', 't10k-labels-idx1-ubyte.gz'),
        ('index', 'train-images-idx3-ubyte.gz'),
        ('query', 't10k-images-idx3-ubyte.gz')
    ]
    data_dir = './data'
    url_str = 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/'
    os.makedirs(data_dir, exist_ok=True)
    targets = {
        k: {
            'url': url_str + fn,
            'filename': os.path.join(data_dir, k)
        } for k, fn in target_tuple
    }
    download_data(targets)
    return targets


def index_generator(num_doc: int, doc_dict: dict):
    for j in range(num_doc):
        label_int = doc_dict['index-labels']['data'][j][0]
        if label_int < 3:  # We are using only 3 categories, no need to index the rest
            with Document() as d:
                d.content = doc_dict['index']['data'][j]
                category = get_mapped_label(label_int)
                d.tags['label'] = category
            yield d


def query_generator(num_doc: int, target: dict):
    for j in range(num_doc):
        n = random.randint(0, 9999)  # there are 10000 query examples, so that's the limit
        label_int = target['query-labels']['data'][n][0]
        category = get_mapped_label(label_int)
        if category == 'Pullover':
            d = Document(content=(target['query']['data'][n]))
            d.tags['label'] = category
            yield d


def index(num_doc, target: dict):
    f = Flow.load_config('flows/index.yml')
    with f:
        with TimeContext(f'QPS: indexing {num_doc}', logger=f.logger):
            f.index(index_generator(num_doc, target), request_size=2048)


def query(num_doc, target: dict):
    f = Flow.load_config('flows/query.yml')
    with f:
        with TimeContext(f'QPS: query with {num_doc}', logger=f.logger):
            f.search(query_generator(num_doc, target), shuffle=True, size=128,
                     on_done=print_result, request_size=32, top_k=TOP_K)
    write_html(os.path.join('./workspace', 'hello-world.html'))


def config(task):
    shards_encoder = 2 if task == 'index' else 1
    shards_indexer = 1
    os.environ['JINA_RESOURCE_DIR'] = resource_filename('jina', 'resources')
    os.environ['JINA_SHARDS_INDEXER'] = str(shards_indexer)
    os.environ['JINA_SHARDS_ENCODER'] = str(shards_encoder)
    os.environ['JINA_WORKDIR'] = './workspace'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45683))


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs_query', '-n', default=100)
@click.option('--num_docs_index', '-n', default=600)
def main(task, num_docs_query, num_docs_index):
    config(task)
    logger = JinaLogger('fashion-example-query')
    targets = download_fashionmnist()
    workspace = os.environ['JINA_WORKDIR']
    if task == 'index':
        if os.path.exists(workspace):
            logger.error(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
            sys.exit(1)
        index(num_docs_index, targets)
    elif task == 'query':
        if not os.path.exists(workspace):
            logger.error(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
            sys.exit(1)
        query(num_docs_query, targets)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
