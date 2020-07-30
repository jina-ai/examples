__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import random
import string

import click
from jina.flow import Flow

RANDOM_SEED = 10
random.seed(RANDOM_SEED)


def get_random_ws(workspace_path, length=8):
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)

def print_topk(resp, word):
    for d in resp.search.docs:
        print(f'Ta-Dah🔮, here are what we found for: {word}')
        for idx, kk in enumerate(d.matches):
            score = kk.score.value
            if score < 0.0:
                continue
            doc = kk.match_doc.text
            name, line = doc.split('[SEP]', maxsplit=1)
            print('> {:>2d}({:.2f}). {} said, "{}"'.format(idx, score, name.upper(), line.strip()))


def config(num_docs,mode='index'):
    os.environ['PARALLEL'] = os.environ.get('PARALLEL', str(2) if mode == 'index' else str(1))
    os.environ['SHARDS'] = os.environ.get('SHARDS', str(1))
    os.environ['MAX_NUM_DOCS'] = os.environ.get('MAX_NUM_DOCS', str(num_docs))
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))


def index(num_docs):
    config(num_docs, mode = 'index')
    data_path = os.path.join(os.environ['DATA_DIR'], os.environ['DATA_FILE'])
    f = Flow().load_config('flow-index.yml')
    with f:
        f.index_lines(filepath=data_path, batch_size=8, size=int(os.environ['MAX_NUM_DOCS']))

def query(num_docs, top_k):
    config(num_docs, mode = 'search')
    f = Flow().load_config('flow-query.yml')
    with f:
        while True:
            text = input('please type a sentence: ')
            if not text:
                break
            ppr = lambda x: print_topk(x, text)
            f.search_lines(lines=[text, ], output_fn=ppr, topk=top_k)

def query_restful(num_docs):
    config(num_docs, mode = 'search')
    f = Flow().load_config('flow-query.yml')
    f.use_rest_gateway()
    with f:
        f.block()


def dryrun(num_docs):
    config(num_docs, mode = 'dryrun')
    f = Flow().load_config('flow-index.yml')
    with f:
        f.dry_run()



@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
@click.option('--top_k', '-k', default=5)
def main(task, num_docs, top_k):
    os.environ['DATA_DIR'] = os.environ.get('DATA_DIR', '/tmp/jina/southpark')
    os.environ['DATA_FILE'] = os.environ.get('DATA_FILE', 'character-lines.csv')
    os.environ['TMP_WORKSPACE'] = os.environ.get('TMP_WORKSPACE', get_random_ws(os.environ['DATA_DIR']))
    if task == 'index':
        index(num_docs)
    elif task == 'query':
        query(num_docs, top_k)
    elif task == 'query_restful':
        query_restful(num_docs)
    elif task == 'dryrun':
        dryrun(num_docs)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task should be `index` or `query` or `query_restful` or `dryrun`.')


if __name__ == '__main__':
    main()
