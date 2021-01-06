__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__version__ = '0.0.1'

import csv
import os
import sys
import itertools

from jina.flow import Flow
from jina import Document


def config():
    parallel = 2 if sys.argv[1] == 'index' else 1

    os.environ.setdefault('JINA_MAX_DOCS', '100')
    os.environ.setdefault('JINA_PARALLEL', str(parallel))
    os.environ.setdefault('JINA_SHARDS', str(4))
    os.environ.setdefault('JINA_WORKSPACE', './workspace')
    os.environ.setdefault('JINA_PORT', str(65481))


def input_fn():
    lyrics_file = os.environ.setdefault(
        'JINA_DATA_PATH', 'toy-data/lyrics-toy-data1000.csv'
    )
    with open(lyrics_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in itertools.islice(reader, int(os.environ['JINA_MAX_DOCS'])):
            if row[-1] == 'ENGLISH':
                with Document() as d:
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


def main():
    if len(sys.argv) < 2:
        print('choose between "index/search/dryrun" mode')
        exit(1)

    config()
    if sys.argv[1] == 'index':
        workspace = os.environ['JINA_WORKSPACE']
        if os.path.exists(workspace):
            print(
                f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+'
            )
            sys.exit(1)
        index()
    elif sys.argv[1] == 'search':
        search()
    elif sys.argv[1] == 'dryrun':
        dryrun()
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')


if __name__ == '__main__':
    main()
