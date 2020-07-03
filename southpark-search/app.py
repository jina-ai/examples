__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import random
import string

import click
from jina.flow import Flow

RANDOM_SEED = 10
random.seed(RANDOM_SEED)

os.environ['REPLICAS'] = str(2)
os.environ['SHARDS'] = str(2)
os.environ['TMP_DATA_DIR'] = '/tmp/jina/southpark'
os.environ['JINA_PORT'] = str('45678')


def get_random_ws(workspace_path, length=8):
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)


def print_topk(resp, word):
    for d in resp.search.docs:
        print(f'Ta-Dah🔮, here are what we found for: {word}')
        for idx, kk in enumerate(d.topk_results):
            score = kk.score.value
            if score < 0.0:
                continue
            doc = kk.match_doc.text
            name, line = doc.split('[SEP]', maxsplit=1)
            print('> {:>2d}({:.2f}). {} said, "{}"'.format(idx, score, name.upper(), line.strip()))


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
@click.option('--top_k', '-k', default=5)
def main(task, num_docs, top_k):
    os.environ['TMP_WORKSPACE'] = get_random_ws(os.environ['TMP_DATA_DIR'])
    data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'character-lines.csv')
    if task == 'index':
        f = Flow().load_config('flow-index.yml')
        with f:
            f.index_lines(filepath=data_path, size=num_docs, batch_size=8)
    elif task == 'query':
        f = Flow().load_config('flow-query.yml')
        with f:
            while True:
                text = input('please type a sentence: ')
                if not text:
                    break
                ppr = lambda x: print_topk(x, text)
                f.search_lines(lines=[text, ], output_fn=ppr, topk=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
