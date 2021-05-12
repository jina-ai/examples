__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

import click
from collections import defaultdict

import numpy as np

from jina import Document, Flow
from jina.logging.profile import TimeContext
from jina.logging import JinaLogger
from jina.helloworld.helper import download_data, write_html, print_result

from pkg_resources import resource_filename

TOP_K = 10
num_docs_evaluated = 0
evaluation_value = defaultdict(float)


def download_fashionmnist():
    target_tuple = [
        ('index-labels', 'train-labels-idx1-ubyte.gz'),
        ('query-labels', 't10k-labels-idx1-ubyte.gz'),
        ('index', 'train-images-idx3-ubyte.gz'),
        ('query', 't10k-images-idx3-ubyte.gz')
    ]
    data_dir = os.path.join(os.environ['JINA_WORKDIR'], 'data')
    url_str = 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/'
    targets = {
        k: {
            'url': url_str + fn,
            'filename': os.path.join(data_dir, k)
        } for k, fn in target_tuple
    }
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        download_data(targets)
    else:
        from jina.helloworld.helper import load_mnist, load_labels
        for k, v in targets.items():
            if k == 'index-labels' or k == 'query-labels':
                v['data'] = load_labels(v['filename'])
            if k == 'index' or k == 'query':
                v['data'] = load_mnist(v['filename'])
    return targets


def _doc_generator(num_doc: int, doc_dict: dict, selected_label_id: []):
    label_id = {
        0: 'T-shirt/top',
        1: 'Trouser',
        2: 'Pullover'
    }
    selected_doc_dict = []
    for data, label in zip(doc_dict['query']['data'], doc_dict['query-labels']['data']):
        label = label[0]
        if selected_label_id and label in selected_label_id:
            d = Document(content=data)
            d.tags['label'] = label_id[label]
            selected_doc_dict.append(d)
    selected_id = np.random.permutation(range(len(selected_doc_dict)))
    for idx in selected_id[:num_doc]:
        yield selected_doc_dict[idx]


def index_generator(num_doc: int, doc_dict: dict):
    return _doc_generator(num_doc, doc_dict, [0, 1, 2])


def query_generator(num_doc: int, doc_dict: dict):
    return _doc_generator(num_doc, doc_dict, [2, ])


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
    write_html(os.path.join(os.getenv('JINA_WORKDIR'), 'hello-world.html'))


def config(task):
    shards_encoder = 2 if task == 'index' else 1
    shards_indexer = 1
    os.environ['JINA_RESOURCE_DIR'] = resource_filename('jina', 'resources')
    os.environ['JINA_SHARDS_INDEXER'] = os.getenv('JINA_SHARDS_INDEXER', str(shards_indexer))
    os.environ['JINA_SHARDS_ENCODER'] = os.getenv('JINA_SHARDS_ENCODER', str(shards_encoder))
    os.environ['JINA_WORKDIR'] = os.environ.get('JINA_WORKDIR', './workspace')
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45683))


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs_query', '-n', default=100)
@click.option('--num_docs_index', '-n', default=600)
def main(task, num_docs_query, num_docs_index):
    config(task)
    logger = JinaLogger('fashion-example-query')
    workspace = os.environ['JINA_WORKDIR']
    if task == 'index':
        if os.path.exists(workspace):
            logger.error(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
            sys.exit(1)
    targets = download_fashionmnist()
    if task == 'index':
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
