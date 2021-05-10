__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
import click

from jina.flow import Flow

MAX_DOCS = int(os.environ.get('JINA_MAX_DOCS', 50))
image_src = 'data/**/*.jpg'


def config():
    num_encoders = 1 if sys.argv[1] == 'index' else 1
    shards = 8

    os.environ["JINA_DATA_PATH"] = os.environ.get("JINA_DATA_PATH", "data/*/**.jpg")
    os.environ['JINA_SHARDS'] = str(num_encoders)
    os.environ['JINA_SHARDS_INDEXERS'] = str(shards)
    os.environ['JINA_WORKSPACE'] = './workspace'
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


# for index
def index():
    f = Flow.load_config('flows/index.yml')

    with f:
        f.index_files(image_src, request_size=64, read_mode='rb', size=MAX_DOCS)


# for search
def search():
    f = Flow.load_config('flows/query.yml')

    with f:
        f.block()


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
            sys.exit()
        index()
    elif sys.argv[1] == 'search':
        config()
        search()
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
