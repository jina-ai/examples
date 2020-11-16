__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import click
import os
import string
import random

from jina.flow import Flow

RANDOM_SEED = 10  # 5
os.environ['PARALLEL'] = str(1)
os.environ['SHARDS'] = str(1)


def get_random_ws(workspace_path, length=8):
    random.seed(RANDOM_SEED)
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)


def print_topk(resp, word):
    for d in resp.search.docs:
        print(f'Ta-Dah🔮, here are what we found for: {word}')
        for idx, match in enumerate(d.matches):
            score = match.score.value
            if score <= 0.0:
                continue
            word_def = match.chunks[0].text
            word = match.meta_info.decode()
            print('> {:>2d}({:.2f}). {}: "{}"'.format(idx, score, word, word_def.strip()))


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
@click.option('--top_k', '-k', default=5)
def main(task, num_docs, top_k):
    workspace_path = '/tmp/jina/urbandict'
    os.environ['WORKDIR'] = get_random_ws(workspace_path)
    data_fn = os.environ.get('WASHED_DATA_DIR', os.path.join(workspace_path, 'urbandict-word-defs.csv'))
    if task == 'index':
        workspace = os.environ['WORKDIR']
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
        f = Flow().load_config('flow-index.yml')
        with f:
            f.index_lines(filepath=data_fn, size=num_docs, batch_size=16)
    elif task == 'query':
        f = Flow().load_config('flow-query.yml')
        with f:
            while True:
                text = input('word definition: ')
                if not text:
                    break
                ppr = lambda x: print_topk(x, text)
                f.search_lines(lines=[text, ], output_fn=ppr, top_k=top_k)
    elif task == 'query_restful':
        f = Flow().load_config('flow-query.yml')
        f.use_rest_gateway()
        with f:
            f.block()
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is `index` or `query` or `query_restful`.')


if __name__ == '__main__':
    main()
