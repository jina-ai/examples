__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

from jina.flow import Flow
num_docs = os.environ.get('MAX_DOCS', 50000)
image_src = 'data/**/*.png'


def config():
    parallel = 1 if sys.argv[1] == 'index' else 1
    shards = 1

    os.environ['PARALLEL'] = str(parallel)
    os.environ['SHARDS'] = str(shards)
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


# for index
def index():
    # from jina.clients.python import PyClient
    # PyClient.check_input(input_fn())

    f = Flow.load_config('flow-index.yml')

    with f:
        f.index_files(image_src, batch_size=64, read_mode='rb', size=num_docs)


# for search
def search():
    f = Flow.load_config('flow-query.yml')

    with f:
        f.block()


# for test before put into docker
def dryrun():
    f = Flow.load_config('flow-query.yml')

    with f:
        pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('choose between "index" and "search" mode')
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
