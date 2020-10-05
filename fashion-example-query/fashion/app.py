__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

import urllib.request
import gzip
import numpy as np
import webbrowser
import random


from jina.flow import Flow
from jina.clients.python import ProgressBar
from jina.helper import colored
from jina.logging import default_logger
from jina.proto import jina_pb2
from jina.drivers.helper import array2pb

from pkg_resources import resource_filename
from components import *

result_html = []

label_id = {
    0: 'T-shirt/top',
    1: 'Trouser',
    2: 'Pullover',
    3: 'Dress',
    4: 'Coat',
    5: 'Sandal',
    6: 'Shirt',
    7: 'Sneaker',
    8: 'Bag',
    9: 'Ankle boot'
}


def get_mapped_label(label_int):
    """
    Get a label_int and return the description of that label
    label_int	Description
    0	        T-shirt/top
    1	        Trouser
    2	        Pullover
    3	        Dress
    4	        Coat
    5	        Sandal
    6	        Shirt
    7	        Sneaker
    8	        Bag
    9	        Ankle boot
    """
    return label_id.get(label_int, "Invalid tag")


def print_result(resp):
    for d in resp.search.docs:
        vi = d.uri
        result_html.append(f'<tr><td><img src="{vi}"/></td><td>')
        for kk in d.matches:
            kmi = kk.uri
            result_html.append(f'<img src="{kmi}" style="opacity:{kk.score.value}"/>')
            # k['score']['explained'] = json.loads(kk.score.explained)
        result_html.append('</td></tr>\n')


def write_html(html_path):
    with open(resource_filename('jina', '/'.join(('resources', 'helloworld.html'))), 'r') as fp, \
            open(html_path, 'w') as fw:
        t = fp.read()
        t = t.replace('{% RESULT %}', '\n'.join(result_html))
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


def load_mnist(path):
    with gzip.open(path, 'rb') as fp:
        return np.frombuffer(fp.read(), dtype=np.uint8, offset=16).reshape([-1, 784])


def load_labels(path):
    with gzip.open(path, 'rb') as fp:
        return np.frombuffer(fp.read(), dtype=np.uint8, offset=8).reshape([-1, 1])


def download_data(target, download_proxy=None):
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


def index_generator(num_doc, target):
    for j in range(num_doc):
        label_int = target['index-labels']['data'][j][0]
        d = jina_pb2.Document()
        d.blob.CopyFrom(array2pb((target['index']['data'][j])))
        d.tags.update({'label': get_mapped_label(label_int)})
        yield d


def query_generator(num_doc, target):
    for j in range(num_doc):
        n = random.randint(0, 10000) #there are 10000 query examples, so that's the limit
        d = jina_pb2.Document()
        label_int = targets['query-labels']['data'][n][0]
        d.blob.CopyFrom(array2pb(target['query']['data'][n]))
        d.tags.update({'label': get_mapped_label(label_int)})
        yield d


def index(num_doc, target):
    f = Flow.load_config('flow-index.yml')
    with f:
        f.index(index_generator(num_doc, target), batch_size=2048)


def query(num_doc, target):
    f = Flow.load_config('flow-query.yml')
    with f:
        f.search(query_generator(num_doc, target), shuffle=True, size=128,
                 output_fn=print_result, batch_size=32)
    write_html(os.path.join('./workspace', 'hello-world.html'))


def config():
    parallel = 2 if sys.argv[1] == 'index' else 1
    shards = 1
    os.environ['RESOURCE_DIR'] = resource_filename('jina', 'resources')
    os.environ['SHARDS'] = str(shards)
    os.environ['PARALLEL'] = str(parallel)
    os.environ['HW_WORKDIR'] = './workspace'
    os.makedirs(os.environ['HW_WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45683))


if __name__ == '__main__':

    if not os.path.exists('./workspace'):
        os.makedirs('./workspace')
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
    num_docs_index = 60000
    num_docs_query = 100

    config()

    if len(sys.argv) < 2:
        print('choose between "index" and "search" mode')
        exit(1)
    if sys.argv[1] == 'index':
        config()
        index(num_docs_index, targets)
    elif sys.argv[1] == 'query':
        config()
        query(num_docs_query, targets)
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
