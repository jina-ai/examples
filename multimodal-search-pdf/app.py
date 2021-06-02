__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
import glob
import click
from jina import Document, Flow
from jina.logging.profile import TimeContext
from jina.logging import default_logger as logger

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
    print(f'### {[m.uri for m in resp.docs[0].matches]}')


def index(pdf_files):
    f = Flow.load_config('flows/index.yml')
    with f:
        with TimeContext(f'QPS: indexing {len(pdf_files)}', logger=f.logger):
            f.post('/index', inputs=index_generator(pdf_files))
            # f.index(inputs=index_generator(data_path=pdf_files), read_mode='r', on_done=pprint_routes,
            #        request_size=1)


def query():
    f = Flow.load_config('flows/query-multimodal.yml')
    # f.plot()
    with f:
        with TimeContext(f'QPS: query with {3}', logger=f.logger):
            d = Document()
            search_text = 'It makes sense to first define whata we mean by multimodality before going into morefancy terms.'  # blog1
            # search_text = 'We all know about CRUD[1]. Every app out there does it.'#blog2
            # search_text = 'Developing a Jina app often means writing YAML configs.'#blog3
            search_text = 'Let’s say you have the image on the left.'
            d.text = search_text
            # There are three ways to search.
            print('text search:')
            f.search(inputs=d, on_done=get_pdf)
            print('image search:')
            f.search(inputs=search_generator(data_path='toy_data/photo-1.png'), read_mode='r', on_done=get_pdf)
            print('pdf search:')
            f.search(inputs=search_generator(data_path='toy_data/blog2-pages-1.pdf'), read_mode='r', on_done=get_pdf)


def query_text():
    f = Flow.load_config('flows/query-only-text.yml')
    with f:
        # search_text = 'It makes sense to first define what we mean by multimodality before going into more fancy terms.'  # blog1
        search_text = 'We all know about CRUD[1]. Every app out there does it.'#blog2
        #search_text = 'Developing a Jina app often means writing YAML configs.'  # blog3
        d = Document(text=search_text)
        f.post('/search', inputs=d, on_done=get_pdf)


def query_image():
    f = Flow.load_config('flows/query-only-image.yml')
    with f:
        print('image search:')
        f.search(inputs=search_generator(data_path='toy_data/photo-1.png'), read_mode='r', on_done=get_pdf)


def query_pdf():
    f = Flow.load_config('flows/query-only-pdf.yml')
    with f:
        print('pdf search:')
        f.search(inputs=search_generator(data_path='toy_data/blog2-pages-1.pdf'), read_mode='r', on_done=get_pdf)


def query_multi_modal_pdf():
    f = Flow.load_config('flows/query.yml')
    with f:
        f.search(inputs=search_generator(data_path='toy_data/blog2-pages-1.pdf'), read_mode='r', on_done=get_pdf)


def query_multi_modal_text():
    f = Flow.load_config('flows/query.yml')
    search_text = 'It makes sense to first define what we mean by multimodality before going into more fancy terms.'  # blog1
    doc = Document(text=search_text)

    with f:
        f.post('/search', inputs=doc, on_done=get_pdf)


def query_multi_modal_image():
    f = Flow.load_config('flows/query.yml')
    with f:
        f.search(inputs=search_generator(data_path='toy_data/photo-1.png'), read_mode='r', on_done=get_pdf)


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
            logger.error(f'\n +---------------------------------------------------------------------------------+ \
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
        query_multi_modal_text()
    if task == 'query_image':
        query_multi_modal_image()
    if task == 'query_pdf':
        query_multi_modal_pdf()
    if task == 'query_restful':
        f = Flow.load_config('flows/query.yml')
        f.use_rest_gateway()
        with f:
            f.block()


if __name__ == "__main__":
    main()
