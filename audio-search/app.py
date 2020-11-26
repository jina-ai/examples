__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__version__ = '0.0.1'

import os
import click

from jina.flow import Flow


def config(task):
    parallel = 2 if task == 'index' else 1
    os.environ['PARALLEL'] = str(parallel)
    os.environ['SHARDS'] = str(1)
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))

@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=100)
def main(task, num_docs):
    config(task)
    if task == 'index':
        workspace = os.environ['WORKDIR']
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
        f = Flow.load_config('flows/index.yml')
        with f:
            f.index_files('data/*.wav', batch_size=2, size=num_docs)
    elif task == 'query':
        f = Flow.load_config('flows/query.yml')
        with f:
            f.block()
    elif task == 'dryrun':
        f = Flow.load_config('flows/query.yml')
        with f:
            pass
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query` or `dryrun`.')


if __name__ == '__main__':
    main()
