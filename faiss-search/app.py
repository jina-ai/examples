__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import Generator, Any

import click
import os
import string
import random
import numpy as np

from fvecs_read import fvecs_read
from jina.flow import Flow

RANDOM_SEED = 14
os.environ['REPLICAS'] = str(1)
os.environ['SHARDS'] = str(1)
os.environ['TMP_DATA_DIR'] = '/tmp/jina/faiss/siftsmall'


def get_random_ws(workspace_path, length=8):
    random.seed(RANDOM_SEED)
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)


def read_data(db_file_path: str) -> Generator[bytes, Any, Any]:
    vectors = fvecs_read(db_file_path)
    num_vectors = vectors.shape[0]
    for i in range(1, num_vectors + 1):
        start_batch = (i - 1)
        end_batch = i if i < num_vectors else num_vectors
        yield vectors[start_batch: end_batch].tobytes()


def save_topk(resp, output_fn=None):
    results = []
    for d in resp.search.docs:
        cur_result = []
        d_fn = d.meta_info.decode()
        cur_result.append(d_fn)
        print("-" * 20)
        print('query vector: {}'.format(np.frombuffer(d.blob.buffer, d.blob.dtype)))
        print('matched vectors' + "*" * 10)
        for idx, kk in enumerate(d.topk_results):
            score = kk.score.value
            if score < 0.0:
                continue
            m_fn = np.frombuffer(kk.match_doc.blob.buffer, kk.match_doc.blob.dtype)
            print('{:>2d}:({:f}):{}'.format(
                idx, score, m_fn))
            cur_result.append(m_fn)
        results.append(cur_result)


@click.command()
@click.option('--task', '-t')
@click.option('--batch_size', '-n', default=50)
@click.option('--top_k', '-k', default=5)
def main(task, batch_size, top_k):
    os.environ['TMP_WORKSPACE'] = get_random_ws(os.environ['TMP_DATA_DIR'])
    if task == 'index':
        data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'siftsmall_base.fvecs')
        flow = Flow().load_config('flow-index.yml')
        with flow.build() as fl:
            fl.index(read_data(data_path), batch_size=batch_size)
    elif task == 'query':
        data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'siftsmall_query.fvecs')
        flow = Flow().load_config('flow-query.yml')
        with flow.build() as fl:
            ppr = lambda x: save_topk(x, os.path.join(os.environ['TMP_DATA_DIR'], 'query_results.txt'))
            fl.search(buffer=read_data(data_path), callback=ppr, top_k=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
