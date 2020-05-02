__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import random
import os
import click
import string
from jina.flow import Flow

RANDOM_SEED = 10
random.seed(RANDOM_SEED)

os.environ['REPLICAS'] = str(1)
os.environ['SHARDS'] = str(1)
os.environ['TMP_DATA_DIR'] = '/tmp/jina/southpark'


def get_random_ws(workspace_path, length=8):
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)


def read_data(f_path, max_sample_size=-1):
    if not os.path.exists(f_path):
        print('file not found: {}'.format(f_path))
    doc_list = []
    with open(f_path, 'r') as f:
        for l in f:
            doc_list.append(l.strip('\n'))
    if max_sample_size > 0:
        random.shuffle(doc_list)
        doc_list = doc_list[:max_sample_size]
    for d in doc_list:
        yield d.encode('utf8')


def print_topk(resp, word):
    for d in resp.search.docs:
        print(f'Ta-Dah🔮, here are what we found for: {word}')
        for idx, kk in enumerate(d.topk_results):
            score = kk.score.value
            if score < 0.0:
                continue
            doc = kk.match_doc.raw_bytes.decode()
            name, line = doc.split('!', maxsplit=1)
            print('> {:>2d}({:.2f}). {} said, "{}"'.format(idx, score, name.upper(), line.strip()))


def read_query_data(text):
    yield '{}'.format(text).lower().encode('utf8')


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
@click.option('--top_k', '-k', default=5)
def main(task, num_docs, top_k):
    os.environ['TMP_WORKSPACE'] = get_random_ws(os.environ['TMP_DATA_DIR'])
    data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'character-lines.csv')
    if task == 'index':
        flow = Flow().load_config('flow-index.yml')
        with flow.build() as fl:
            fl.index(raw_bytes=read_data(data_path, num_docs), batch_size=8)
        print('done')
    elif task == 'query':
        flow = Flow().load_config('flow-query.yml')
        with flow.build() as fl:
            while True:
                text = input('please type a sentence: ')
                if not text:
                    break
                ppr = lambda x: print_topk(x, text)
                fl.search(read_query_data(text), callback=ppr, topk=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
