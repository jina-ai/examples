__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

import click
import requests
from jina import Document
from jina.clients.sugary_io import _input_lines
from jina.flow import Flow
from jina.logging import JinaLogger
from jina.logging.profile import TimeContext

MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 50))


def config():
    os.environ["JINA_DATA_FILE"] = os.environ.get("JINA_DATA_FILE", "data/toy-data.txt")
    os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "workspace")
    os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))


def print_topk(resp, sentence):
    for d in resp.search.docs:
        print(f"Ta-Dah🔮, here are what we found for: {sentence}")
        for idx, match in enumerate(d.matches):

            score = match.score.value
            if score < 0.0:
                continue
            print(f'> {idx:>2d}({score:.2f}). {match.text}')


def index(num_docs):
    f = Flow().load_config("flows/index.yml")

    with f:
        data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None))
        with TimeContext(f'QPS: indexing {num_docs}', logger=f.logger):
            f.index_lines(filepath=data_path, batch_size=16, read_mode='r', size=num_docs)

def index_restful(num_docs):
    f = Flow().load_config('flows/index.yml')

    with f:
        data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None))
        f.logger.info(f'Indexing {data_path}')
        url = f'http://0.0.0.0:{f.port_expose}/index'

        input_docs = _input_lines(
            filepath=data_path,
            size=num_docs,
            read_mode='r',
        )
        data_json = {'data': [Document(text=text).dict() for text in input_docs]}
        r = requests.post(url, json=data_json)
        if r.status_code != 200:
            raise Exception(f'api request failed, url: {url}, status: {r.status_code}, content: {r.content}')

def query(top_k):
    f = Flow().load_config("flows/query.yml")
    with f:
        while True:
            text = input("please type a sentence: ")
            if not text:
                break

            with TimeContext(f'QPS: query with 1', logger=f.logger):
                f.search_lines(lines=[text, ], line_format='text', top_k=top_k)


def query_restful():
    f = Flow().load_config("flows/query.yml")
    f.use_rest_gateway()
    with f:
        f.block()


def dryrun():
    f = Flow().load_config("flows/index.yml")
    with f:
        f.dry_run()


@click.command()
@click.option(
    "--task",
    "-t",
    type=click.Choice(
        ["index", "index_restful", "query", "query_restful", "dryrun"], case_sensitive=False
    ),
)
@click.option("--num_docs", "-n", default=MAX_DOCS)
@click.option("--top_k", "-k", default=5)
def main(task, num_docs, top_k):
    config()
    workspace = os.environ["JINA_WORKSPACE"]
    logger = JinaLogger('chinese-text-search')
    if 'index' in task:
        if os.path.exists(workspace):
            logger.error(
                f'\n +------------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                           | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                           | \
                    \n +------------------------------------------------------------------------------------+'
            )
            sys.exit(1)

    logger.info(f'### task = {task}')
    if task == "index":
        index(num_docs)
    elif task == "index_restful":
        index_restful(num_docs)
    elif task == "query":
        if not os.path.exists(workspace):
            logger.warning(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
        query(top_k)
    elif task == "query_restful":
        if not os.path.exists(workspace):
            logger.warning(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
        query_restful()
    elif task == "dryrun":
        dryrun()


if __name__ == "__main__":
    main()
