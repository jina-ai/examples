__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import sys
import os

from jina.flow import Flow


def config(mode='index'):
    os.environ['REPLICAS'] = str(2) if mode == 'index' else str(1)
    os.environ['SHARDS'] = str(8)
    os.environ['TMP_WORKSPACE'] = os.environ.get('TMP_WORKSPACE', './workspace')
    os.environ['DATA_DIR'] = os.environ.get('DATA_DIR', './data')
    os.environ['DATA_FILE'] = os.environ.get('DATA_FILE', 'character-lines.csv')
    os.environ['MAX_NUM_DOCS'] = os.environ.get('MAX_NUM_DOCS', str(106819))
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def print_error():
    print('USAGE: python app.py [index|search]')


def index():
    data_path = os.path.join(os.environ['DATA_DIR'], os.environ['DATA_FILE'])
    f = Flow().load_config('flow-index.yml')
    with f:
        f.index_lines(filepath=data_path, batch_size=8, size=int(os.environ['MAX_NUM_DOCS']))


def search():
    f = Flow().load_config('flow-query.yml')
    with f:
        f.block()


def dryrun():
    f = Flow().load_config('flow-index.yml')
    with f:
        f.dry_run()


def main():
    if len(sys.argv) < 2:
        print_error()
        exit(1)
    config(sys.argv[1])
    if sys.argv[1] == 'index':
        index()
    elif sys.argv[1] == 'search':
        search()
    elif sys.argv[1] == 'dryrun':
        dryrun()
    else:
        print_error()
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')


if __name__ == '__main__':
    main()
