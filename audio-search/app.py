__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import os
import sys

import click
from jina.flow import Flow
from jina.logging.profile import TimeContext


def config():
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_SHARDS', str(4))
    os.environ['JINA_WORKSPACE'] = os.environ.get('JINA_WORKSPACE', './workspace')
    os.environ['JINA_DATA_FILE'] = os.environ.get('JINA_DATA_FILE', 'data/*.wav')
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))
    os.environ['JINA_TOPK'] = os.environ.get('JINA_TOPK', str(5))


@click.command()
@click.option(
    '--task',
    '-t',
    type=click.Choice(["index", "query","query_restful"], case_sensitive=False))
@click.option('--num_docs', '-n', default=100)
def main(task, num_docs):
    config()
    workspace = os.environ['JINA_WORKSPACE']
    if task == 'index':
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
            sys.exit(1)
        f = Flow.load_config('flows/index.yml')
        with f:
            with TimeContext(f'QPS: indexing', logger=f.logger):
                f.index_files(os.environ.get('JiNA_DATA_FILE'), batch_size=2, size=num_docs)
    if 'query' in task:
        if not os.path.exists(workspace):
            print(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
            sys.exit(1)
    if task == 'query_restful':
        f = Flow.load_config('flows/query.yml')
        f.use_rest_gateway(os.environ.get('JINA_PORT'))
        with f:
            # no perf measurement here, as it opens the REST API and blocks
            f.block()
    if task == 'query':
        f = Flow.load_config('flows/query.yml')
        with f:
            with TimeContext(f'QPS: querying', logger=f.logger):
                f.search_files(os.environ.get('JiNA_DATA_FILE'), size=num_docs, on_done=get_top_match)


def get_top_match(resp):
    # note that this is only for validating the results at console
    print(len(resp.search.docs[0].matches))
    for m in resp.search.docs[0].matches:
        print(m.mime_type)


if __name__ == '__main__':
    main()
