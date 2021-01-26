__copyright__ = "Copyright (c) 2020 - 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
from glob import glob

from jina.flow import Flow

GIF_BLOB = 'data/*.gif'
LEN_DOCS = len(glob(GIF_BLOB))
# allows for returning all docs
JINA_TOPK = 5000
# TODO test w 2
SHARDS_DOC = 1
SHARDS_CHUNK_SEG = 1


def config():
    shards = 1
    os.environ['JINA_TOPK'] = str(JINA_TOPK)
    os.environ['SHARDS_DOC'] = str(SHARDS_DOC)
    os.environ['SHARDS_CHUNK_SEG'] = str(SHARDS_CHUNK_SEG)
    os.environ['SHARDS_INDEXER'] = str(shards)
    os.environ['JINA_WORKSPACE'] = './workspace'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


# for index
def index():
    f = Flow.load_config('flow-index.yml')

    with f:
        f.index_files(GIF_BLOB, request_size=1, read_mode='rb', skip_dry_run=True)


def validate_output(resp):
    print(f'****************** got {len(resp.docs)} documents in response')
    print(f'****************** got {len(resp.docs[0].matches)} documents in doc.matches')
    assert len(resp.docs[0].matches) == LEN_DOCS


# for search
def search():
    f = Flow.load_config('flow-query.yml')

    with f:
        # running one search with one of the files
        f.search_files(glob(GIF_BLOB)[0], on_done=validate_output)
        # waiting for input via REST gateway
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
        workspace = os.environ['JINA_WORKSPACE']
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
            sys.exit(1)
        index()
    elif sys.argv[1] == 'search':
        config()
        search()
    elif sys.argv[1] == 'dryrun':
        config()
        dryrun()
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
