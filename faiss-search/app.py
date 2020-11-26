__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import Generator, Any

import click
import os
import string
import random
import numpy as np

from read_vectors_files import fvecs_read, ivecs_read
from jina.flow import Flow

RANDOM_SEED = 14
os.environ['PARALLEL'] = str(1)
os.environ['SHARDS'] = str(1)
os.environ['TMP_DATA_DIR'] = '/tmp/jina/faiss/siftsmall'


def get_random_ws(workspace_path, length=8):
    random.seed(RANDOM_SEED)
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)


def read_data(db_file_path: str):
    return fvecs_read(db_file_path)


def save_topk(resp, output_file, top_k):
    results = []
    with open(output_file, 'w') as fw:
        query_id = 0
        for d in resp.search.docs:
            result = []
            fw.write('-' * 20)
            fw.write('\n')

            fw.write('query id {}:'.format(query_id))
            fw.write('\n')
            fw.write('matched vectors' + "*" * 10)
            fw.write('\n')
            for idx, match in enumerate(d.matches):
                result.append(match.id)
                score = match.score.value
                if score < 0.0:
                    continue
                m_fn = np.frombuffer(match.blob.buffer, match.blob.dtype)
                fw.write('\n')
                fw.write('Idx: {:>2d}:(DocId {}, Ranking score: {:f}): \n{}'.
                         format(idx, match.id, score, m_fn))
                fw.write('\n')
            fw.write('\n')
            results.append(result)
            query_id += 1
        fw.write(f'recall@{top_k}: {recall_at_k(np.array(results), top_k)}')

    print(open(output_file, 'r').read())


def recall_at_k(results, k):
    """
    Computes how many times the true nearest neighbour is returned as one of the k closest vectors from a query.

    Taken from https://gist.github.com/mdouze/046c1960bc82801e6b40ed8ee677d33e
    """
    groundtruth_path = os.path.join(os.environ['TMP_DATA_DIR'], 'siftsmall_groundtruth.ivecs')
    groundtruth = ivecs_read(groundtruth_path)
    eval = (results[:, :k] == groundtruth[:, :1]).sum() / float(results.shape[0])
    return eval


@click.command()
@click.option('--task', '-t')
@click.option('--batch_size', '-n', default=50)
@click.option('--top_k', '-k', default=5)
def main(task, batch_size, top_k):
    os.environ['WORKDIR'] = get_random_ws(os.environ['TMP_DATA_DIR'])
    if task == 'index':
        data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'siftsmall_base.fvecs')
        if os.path.exists(data_path):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {data_path} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
        
        flow = Flow().load_config('flow-index.yml')
        with flow.build() as fl:
            fl.index_ndarray(read_data(data_path), batch_size=batch_size)
    elif task == 'query':
        data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'siftsmall_query.fvecs')
        flow = Flow().load_config('flow-query.yml')
        with flow.build() as fl:
            ppr = lambda x: save_topk(x, os.path.join(os.environ['TMP_DATA_DIR'], 'query_results.txt'), top_k)
            fl.search_ndarray(read_data(data_path), output_fn=ppr, top_k=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
