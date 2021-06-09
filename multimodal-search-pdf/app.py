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
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))


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


def log_search_results(resp) -> None:
    search_result = ''.join([f'- {match.uri} \n' for match in resp.docs[0].matches])
    logger.info(f'The search returned the following documents \n{search_result}')


def index(num_docs: int) -> None:
    workspace = os.environ['JINA_WORKSPACE']
    if os.path.exists(workspace):
        logger.error(f'\n +---------------------------------------------------------------------------------+ \
                        \n |                                   🤖🤖🤖                                        | \
                        \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                        \n |                                   🤖🤖🤖                                        | \
                        \n +---------------------------------------------------------------------------------+')
        sys.exit(1)
    pdf_files = glob.glob(os.path.join(PDF_DATA_PATH, '*.pdf'))[: num_docs]
    f = Flow.load_config('flows/index.yml')
    with f:
        with TimeContext(f'QPS: indexing {len(pdf_files)}', logger=f.logger):
            f.post('/index', inputs=index_generator(pdf_files))


def query_restful():
    f = Flow.load_config('flows/query.yml')
    f.use_rest_gateway()
    with f:
        f.block()


def query_text():
    f = Flow.load_config('flows/query.yml')
    with f:
        search_text = input('Please type a sentence: ')
        doc = Document(content=search_text, mime_type='text/plain')
        f.post('/search', inputs=doc, on_done=log_search_results)


@click.command()
@click.option(
    "--task",
    "-t",
    type=click.Choice(["index", "query_text", "query_restful"], case_sensitive=False),
)
@click.option("--num_docs", "-n", default=MAX_DOCS)
def main(task, num_docs):
    config()
    if task == 'index':
        index(num_docs)
    if task == 'query_text':
        query_text()
    if task == 'query_restful':
        query_restful()


if __name__ == "__main__":
    main()
