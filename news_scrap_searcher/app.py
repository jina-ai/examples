__version__ = '0.0.1'

import os
import sys

from urllib.parse import urlparse
from newspaper import Article
from jina.flow import Flow

num_docs = int(os.environ.get('MAX_DOCS', 500))


def config():
    """Set up configuration via environment variables."""
    parallel = 2 if sys.argv[1] == 'index' else 1
    shards = 2

    os.environ['JINA_PARALLEL'] = str(parallel)
    os.environ['JINA_SHARDS'] = str(shards)
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))


def index_by_link(url: str):
    """Index new via scrapping. It downloads the link and extrats the title."""
    article = Article(url)
    article.download()
    article.parse()
    title = article.title
    print(f"title:{title}")
    f = Flow.load_config('flows/index.yml')
    with f:
        f.index_lines(lines=[title], batch_size=16,
                      read_mode='r', size=num_docs)
    # for search


def query_restful():
    """Set up REST endpoint."""
    f = Flow().load_config('flows/query.yml')
    f.use_rest_gateway()
    with f:
        f.block()


# for test before put into docker
def dryrun():
    """Dry run for testing."""
    f = Flow.load_config('flows/query.yml')

    with f:
        pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('choose between "index_by_link/rest/dryrun" mode')
        exit(1)
    elif sys.argv[1] == 'index_by_link':
        config()
        index_by_link(sys.argv[2])
    elif sys.argv[1] == 'rest':
        config()
        query_restful()
    elif sys.argv[1] == 'dryrun':
        config()
        dryrun()
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
