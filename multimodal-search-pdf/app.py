__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os

import click
from jina import Document
from jina import Flow

MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 50))


def config():
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45670))


def search_generator(path: str, buffer: bytes):
    d = Document()
    if buffer:
        d.buffer = buffer
    if path:
        d.content = path
    yield d


def dryrun():
    f = Flow().load_config("flows/flow-index.yml")
    with f:
        f.dry_run()


def get_pdf(resp):
    print(resp.search.docs[0].matches[0].mime_type == 'application/pdf')
    print(len(resp.search.docs[0].matches))
    print(resp.search.docs[0].matches)


@click.command()
@click.option(
    "--task",
    "-t",
    type=click.Choice(
        ["index", "query", "query_restful", "dryrun"], case_sensitive=False
    ),
)
@click.option("--num_docs", "-n", default=MAX_DOCS)
@click.option("--top_k", "-k", default=5)
def main(task, num_docs, top_k):
    config()
    if task == 'index':
        f = Flow.load_config('flows/index.yml')
        with f:
            #for pdffile in ['data/blog1.pdf', 'data/blog2.pdf', 'data/blog3.pdf']:
            for pdffile in ['data/1806.05662.pdf', 'data/2103.01937.pdf', 'data/2103.07969.pdf']:
                f.index(input_fn=search_generator(path=pdffile, buffer=None), read_mode='r')

    if task == 'query':
        f = Flow.load_config('flows/query.yml')
        with f:
            d = Document()
            #search_text = 'Unsupervisedly Learned Relational Graphs'
            search_text = 'Neural Production Systems'
            d.text = search_text
            # There are three ways to search.
            print('text search:')
            f.search(input_fn=d, on_done=get_pdf)
            #print('image search:')
            #f.search(input_fn=search_generator(path='data/photo-1.png', buffer=None), read_mode='r',on_done=get_pdf)
            print('pdf search:')
            f.search(input_fn=search_generator(path='data/2103.01937.pdf', buffer=None), read_mode='r',on_done=get_pdf)


if __name__ == "__main__":
    main()
