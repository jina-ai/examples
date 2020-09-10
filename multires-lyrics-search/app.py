__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__version__ = '0.0.1'

import csv
import os
import sys
import itertools

from jina.flow import Flow
from jina.proto import jina_pb2

num_docs = os.environ.get('MAX_DOCS', 500)


def config():
    parallel = 1 if sys.argv[1] == 'index' else 1
    shards = 1

    os.environ['PARALLEL'] = str(parallel)
    os.environ['SHARDS'] = str(shards)
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))


def input_fn():
    with open('toy-data/lyrics-toy-data1000.csv', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in itertools.islice(reader, num_docs):
            if row[-1] == 'ENGLISH':
                d = jina_pb2.Document()
                d.tags['ALink'] = row[0]
                d.tags['SName'] = row[1]
                d.tags['SLink'] = row[2]
                d.text = row[3]
                yield d


# for index
def index():
    f = Flow.load_config('flows/index.yml')

    with f:
        f.index(input_fn, batch_size=8)

    # for search


def search():
    f = Flow.load_config('flows/query.yml')

    with f:
        f.block()


# for test before put into docker
def dryrun():
    f = Flow.load_config('flows/query.yml')

    with f:
        pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('choose between "index/search/dryrun" mode')
        exit(1)
    if sys.argv[1] == 'index':
        config()
        index()
    elif sys.argv[1] == 'search':
        config()
        search()
    elif sys.argv[1] == 'dryrun':
        config()
        dryrun()
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
