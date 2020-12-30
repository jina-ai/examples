__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import os
import click

from jina.flow import Flow


def config(task):
    parallel = 2 if task == 'index' else 1

    os.environ['TMP_WORKSPACE'] = '/tmp/jina/workspace'
    os.environ['COLOR_CHANNEL_AXIS'] = str(0)
    os.environ['SHARDS'] = str(8)
    os.environ['PARALLEL'] = str(parallel)
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45692))


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=500)
def main(task, num_docs):
    config(task)
    workspace = os.environ['WORKDIR']
    image_src = '/tmp/jina/celeb/lfw/**/*.jpg'
    if task == 'index':
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
        f = Flow().load_config('flow-index.yml')
        with f:
            f.index_files(image_src, batch_size=8, read_mode='rb', size=num_docs)
    elif task == 'query':
        f = Flow().load_config('flow-query.yml')
        f.use_rest_gateway()
        with f:
            f.block()
    elif task == 'dryrun':
        f = Flow.load_config('flow-query.yml')
        with f:
            pass
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query` or `dryrun`.')


if __name__ == '__main__':
    main()
