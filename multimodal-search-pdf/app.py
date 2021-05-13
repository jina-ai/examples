__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
import glob
import click
from jina import Document, Flow
from jina.logging.profile import TimeContext

MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 50))
PDF_DATA_PATH = 'toy_data'


def config():
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '2')
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45670))


def index_generator(data_path):
    for path in data_path:
        with Document() as doc:
            doc.content = path
            doc.mime_type = 'application/pdf'
        yield doc


def search_generator(data_path):
    d = Document()
    d.content = data_path
    yield d


def get_pdf(resp):
    # note that this is only for validating the results at console
    print(resp.search.docs[0].matches[0].mime_type == 'application/pdf')
    print(resp.search.docs[0].matches)
    print(len(resp.search.docs[0].matches))


def index(pdf_files):
    f = Flow.load_config('flows/index.yml')
    # f.plot()
    with f:
        with TimeContext(f'QPS: indexing {len(pdf_files)}', logger=f.logger):
            from jina.clients.helper import pprint_routes
            f.index(input_fn=index_generator(data_path=pdf_files), read_mode='r', on_done=pprint_routes,
                    request_size=1)


def query():
    f = Flow.load_config('flows/query-multimodal.yml')
    # f.plot()
    with f:
        with TimeContext(f'QPS: query with {3}', logger=f.logger):
            d = Document()
            search_text = 'It makes sense to first define what we mean by multimodality before going into morefancy terms.'  # blog1
            # search_text = 'We all know about CRUD[1]. Every app out there does it.'#blog2
            # search_text = 'Developing a Jina app often means writing YAML configs.'#blog3
            d.text = search_text
            # There are three ways to search.
            print('text search:')
            f.search(input_fn=d, on_done=get_pdf)
            print('image search:')
            f.search(input_fn=search_generator(data_path='toy_data/photo-1.png'), read_mode='r', on_done=get_pdf)
            print('pdf search:')
            f.search(input_fn=search_generator(data_path='toy_data/blog2-pages-1.pdf'), read_mode='r', on_done=get_pdf)


def query_text():
    f = Flow.load_config('flows/query-only-text.yml')
    with f:
        d = Document()
        search_text = 'It makes sense to first define what we mean by multimodality before going into morefancy terms.'  # blog1
        # search_text = 'We all know about CRUD[1]. Every app out there does it.'#blog2
        # search_text = 'Developing a Jina app often means writing YAML configs.'#blog3
        d.text = search_text
        print('text search:')
        f.search(input_fn=d, on_done=get_pdf)


def query_image():
    f = Flow.load_config('flows/query-only-image.yml')
    with f:
        print('image search:')
        f.search(input_fn=search_generator(data_path='toy_data/photo-1.png'), read_mode='r', on_done=get_pdf)


def query_pdf():
    f = Flow.load_config('flows/query-only-pdf.yml')
    with f:
        print('pdf search:')
        f.search(input_fn=search_generator(data_path='toy_data/blog2-pages-1.pdf'), read_mode='r', on_done=get_pdf)


@click.command()
@click.option(
    "--task",
    "-t",
    type=click.Choice(
        ["index", "query", "query_text", "query_image", "query_pdf", "query_restful"], case_sensitive=False
    ),
)
@click.option("--num_docs", "-n", default=MAX_DOCS)
def main(task, num_docs):
    config()
    if task == 'index':
        workspace = os.environ['JINA_WORKSPACE']
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
            sys.exit(1)
        pdf_files = glob.glob(os.path.join(PDF_DATA_PATH, '*.pdf'))
        index(pdf_files[:num_docs])
    if task == 'query':
        query()
    if task == 'query_text':
        query_text()
    if task == 'query_image':
        query_image()
    if task == 'query_pdf':
        query_pdf()
    if task == 'query_restful':
        f = Flow.load_config('flows/query-multimodal.yml')
        with f:
            f.block()


if __name__ == "__main__":
    main()
