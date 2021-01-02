__version__ = '0.0.1'

import os
import sys

from urllib.parse import urlparse
from newspaper import Article
from jina.flow import Flow

num_docs = int(os.environ.get('MAX_DOCS', 500))


def config():
    parallel = 2 if sys.argv[1] == 'index' else 1
    shards = 2

    os.environ['JINA_PARALLEL'] = str(parallel)
    os.environ['JINA_SHARDS'] = str(shards)
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))


# for index
def index():
    f = Flow.load_config('flows/index.yml')
    with f:
        data_path = os.path.join(os.path.dirname(
            __file__), os.environ.get('JINA_DATA_PATH', None))
        if data_path:
            f.index_lines(filepath=data_path, batch_size=16,
                          read_mode='r', size=num_docs)
        else:
            f.index_lines(lines=['abc', 'cde', 'efg'],
                          batch_size=16, read_mode='r', size=num_docs)


def index_by_link(url: str):
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


def search():
    f = Flow.load_config('flows/query.yml')

    with f:
        f.block()


def query_restful():
    f = Flow().load_config('flows/query.yml')
    f.use_rest_gateway()
    with f:
        f.block()


def query(top_k):
    f = Flow().load_config('flows/query.yml')
    with f:
        while True:
            text = input('please type a sentence: ')
            if not text:
                break

            def ppr(x):
                print_topk(x, text)

            f.search_lines(
                lines=[
                    text,
                ],
                output_fn=ppr,
                top_k=top_k,
            )


def print_topk(resp, sentence):
    for d in resp.search.docs:
        print(f'Ta-Dah🔮, here are what we found for: {sentence}')
        for idx, match in enumerate(d.matches):

            score = match.score.value
            if score < 0.0:
                continue
            # dialog = match.text.strip()
            print(f'> {idx:>2d}({score:.2f}). {match}"')


# for test before put into docker
def dryrun():
    f = Flow.load_config('flows/query.yml')

    with f:
        pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('choose between "index/index_by_link/rest/search/query/dryrun" mode')
        exit(1)
    if sys.argv[1] == 'index':
        config()
        index()
    elif sys.argv[1] == 'index_by_link':
        config()
        # TODO verify urls
        index_by_link(sys.argv[2])
    elif sys.argv[1] == 'query':
        config()
        # TODO verify urls
        query(10)
    elif sys.argv[1] == 'rest':
        config()
        query_restful()
    elif sys.argv[1] == 'search':
        config()
        search()
    elif sys.argv[1] == 'dryrun':
        config()
        dryrun()
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
