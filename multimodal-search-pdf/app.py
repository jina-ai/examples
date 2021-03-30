__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os

import click
from jina import Document
from jina import Flow

MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 50))


def config():
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '4')
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45670))


def search_generator(data_path):
    d = Document()
    d.content = data_path
    yield d

def dryrun():
    f = Flow().load_config("flows/flow-index.yml")
    with f:
        f.dry_run()


def get_pdf(resp):
    # print(resp)
    print(resp.search.docs[0].matches[0].mime_type == 'application/pdf')
    print(len(resp.search.docs[0].matches))
    print(resp.search.docs[0].matches)
    # print(len(resp.search.docs[0].chunks[0].chunks[0].matches))
    # print(resp.search.docs[0].chunks[0].chunks[0].matches)

    # print(len(resp.search.docs[0].chunks[0].matches))
    # print(resp.search.docs[0].chunks[0].matches)


@click.command()
@click.option(
    "--task",
    "-t",
    type=click.Choice(
        ["index", "query", "query_text", "query_image", "query_pdf", "query_restful", "dryrun"], case_sensitive=False
    ),
)
@click.option("--num_docs", "-n", default=MAX_DOCS)
@click.option("--top_k", "-k", default=5)
def main(task, num_docs, top_k):
    config()
    if task == 'index':
        f = Flow.load_config('flows/index.yml')
        f.plot()
        with f:
            from jina.clients.helper import pprint_routes
            pdf_files = ['data/blog1.pdf', 'data/blog2.pdf', 'data/blog3.pdf']
            for path in pdf_files:
                f.index(input_fn=search_generator(data_path=path), read_mode='r', on_done=pprint_routes,
                    request_size=1)
    if task == 'query':
        f = Flow.load_config('flows/query-multimodal.yml')
        f.plot()
        with f:
            d = Document()
            search_text = 'It makes sense to first define what we mean by multimodality before going into morefancy terms.'  # blog1
            # search_text = 'We all know about CRUD[1]. Every app out there does it.'#blog2
            # search_text = 'Developing a Jina app often means writing YAML configs.'#blog3
            d.text = search_text
            # There are three ways to search.
            print('text search:')
            f.search(input_fn=d, on_done=get_pdf)
            print('image search:')
            f.search(input_fn=search_generator(data_path='data/photo-1.png'), read_mode='r', on_done=get_pdf)
            print('pdf search:')
            f.search(input_fn=search_generator(data_path='data/blog2-pages-1.pdf'), read_mode='r', on_done=get_pdf)
    if task == 'query_text':
        f = Flow.load_config('flows/query-only-text.yml')
        with f:
            d = Document()
            search_text = 'It makes sense to first define what we mean by multimodality before going into morefancy terms.'  # blog1
            # search_text = 'We all know about CRUD[1]. Every app out there does it.'#blog2
            # search_text = 'Developing a Jina app often means writing YAML configs.'#blog3
            d.text = search_text
            # we only search text
            print('text search:')
            f.search(input_fn=d, on_done=get_pdf)
    if task == 'query_image':
        f = Flow.load_config('flows/query-only-image.yml')
        with f:
            print('image search:')
            f.search(input_fn=search_generator(data_path='data/photo-1.png'), read_mode='r', on_done=get_pdf)
    if task == 'query_pdf':
        f = Flow.load_config('flows/query-only-pdf.yml')
        with f:
            print('pdf search:')
            f.search(input_fn=search_generator(data_path='data/blog2-pages-1.pdf'), read_mode='r', on_done=get_pdf)
    if task == "dryrun":
        dryrun()


if __name__ == "__main__":
    main()
