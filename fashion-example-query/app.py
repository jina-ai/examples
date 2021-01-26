__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import click
from collections import defaultdict


import urllib.request
import gzip
import numpy as np
import webbrowser
import random

from jina.flow import Flow
from jina.logging.profile import ProgressBar
from jina.helper import colored
from jina.logging import default_logger
from jina.proto import jina_pb2
from jina import Document


from pkg_resources import resource_filename
from components import *

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
    label_int	Description
    0	        T-shirt/top
    1	        Trouser
    2	        Pullover
    """
    return label_id.get(label_int, "Invalid tag")


def print_result(resp):
    for d in resp.search.docs:
        data_uri = d.uri
        result_html.append(f'<tr><td><img src="{data_uri}"/></td><td>')
        for match in d.matches:
            match_uri = match.uri
            result_html.append(f'<img src="{match_uri}"/>')
        result_html.append('</td></tr>\n')

        # update evaluation values
        # as evaluator set to return running avg, here we can simply replace the value
        for evaluation in d.evaluations:
            evaluation_value[evaluation.op_name] = evaluation.value


def write_html(html_path: str):
    global num_docs_evaluated
    global evaluation_value

    with open(resource_filename('jina', '/'.join(('resources', 'helloworld.html'))), 'r') as fp, \
            open(html_path, 'w') as fw:
        t = fp.read()
        t = t.replace('{% RESULT %}', '\n'.join(result_html))
        t = t.replace('{% PRECISION_EVALUATION %}',
            '{:.2f}%'.format(evaluation_value['PrecisionEvaluator'] * 100.0))
        t = t.replace('{% RECALL_EVALUATION %}',
            '{:.2f}%'.format(evaluation_value['RecallEvaluator'] * 100.0))
        t = t.replace('{% TOP_K %}', str(TOP_K))
        fw.write(t)

    url_html_path = 'file://' + os.path.abspath(html_path)

    try:
        webbrowser.open(url_html_path, new=2)
    except:
        pass
    finally:
        default_logger.success(f'You should see a "hello-world.html" opened in your browser, '
                               f'if not you may open {url_html_path} manually')

    colored_url = colored('https://opensource.jina.ai', color='cyan', attrs='underline')
    default_logger.success(
        f'🤩 Intrigued? Play with "jina hello-world --help" and learn more about Jina at {colored_url}')


def load_mnist(path: str):
    with gzip.open(path, 'rb') as fp:
        return np.frombuffer(fp.read(), dtype=np.uint8, offset=16).reshape([-1, 784])


def load_labels(path: str):
    with gzip.open(path, 'rb') as fp:
        return np.frombuffer(fp.read(), dtype=np.uint8, offset=8).reshape([-1, 1])


def download_data(target: dict, download_proxy=None):
    opener = urllib.request.build_opener()
    if download_proxy:
        proxy = urllib.request.ProxyHandler({'http': download_proxy, 'https': download_proxy})
        opener.add_handler(proxy)
    urllib.request.install_opener(opener)
    with ProgressBar(task_name='download fashion-mnist', batch_unit='') as t:
        for k, v in target.items():
            if not os.path.exists(v['filename']):
                urllib.request.urlretrieve(v['url'], v['filename'], reporthook=lambda *x: t.update(1))
            if k == 'index-labels' or k == 'query-labels':
                v['data'] = load_labels(v['filename'])
            if k == 'index' or k == 'query':
                v['data'] = load_mnist(v['filename'])


def index_generator(num_doc: int, target: dict):
    for j in range(num_doc):
        label_int = target['index-labels']['data'][j][0]
        if label_int < 3: #We are using only 3 categories, no need to index the rest
            with Document() as d:
                d.content = target['index']['data'][j]
                category = get_mapped_label(label_int)
                d.tags['label'] = category
            yield d


def query_generator(num_doc: int, target: dict):
    for j in range(num_doc):
        n = random.randint(0, 9999) #there are 10000 query examples, so that's the limit
        label_int = target['query-labels']['data'][n][0] 
        category = get_mapped_label(label_int) 
        if category == 'Pullover':
            d = Document(content=(target['query']['data'][n]))
            d.tags['label'] = category
            yield d


def index(num_doc, target: dict):
    f = Flow.load_config('flows/index.yml')
    with f:
        f.index(index_generator(num_doc, target), request_size=2048)


def query(num_doc, target: dict):
    f = Flow.load_config('flows/query.yml')
    with f:
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
    os.makedirs(os.environ['JINA_WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45683))


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs_query', '-n', default=100)
@click.option('--num_docs_index', '-n', default=600)
def main(task, num_docs_query, num_docs_index):
    config(task)
        
    targets = {
        'index-labels': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-labels-idx1-ubyte.gz',
            'filename': os.path.join('./workspace', 'index-labels')
        },
        'query-labels': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-labels-idx1-ubyte.gz',
            'filename': os.path.join('./workspace', 'query-labels')
        },
        'index': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-images-idx3-ubyte.gz',
            'filename': os.path.join('./workspace', 'index')
        },
        'query': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-images-idx3-ubyte.gz',
            'filename': os.path.join('./workspace', 'query')
        }
    }
    download_data(targets, None)
    if task == 'index':
        config(task)
        workspace = os.environ['JINA_WORKDIR']
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
        index(num_docs_index, targets)
    elif task == 'query':
        config(task)
        query(num_docs_query, targets)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()