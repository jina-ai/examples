import glob
import os
import sys

from jina.flow import Flow

num_docs = 1000000
image_src = 'data/**/*.png'


def config():
    replicas = 2 if sys.argv[1] == 'index' else 1
    shards = 8

    os.environ['REPLICAS'] = str(replicas)
    os.environ['SHARDS'] = str(shards)
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


# for index
def index():
    def input_fn():
        for g in glob.glob(image_src, recursive=True)[:num_docs]:
            with open(g, 'rb') as fp:
                yield fp.read()

    # from jina.clients.python import PyClient
    # PyClient.check_input(input_fn)

    f = Flow.load_config('flow-index.yml')

    with f:
        f.index(input_fn, batch_size=64)


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
