__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import click
import os

import numpy as np
from jina.flow import Flow

from read_vectors_files import fvecs_read, ivecs_read

RANDOM_SEED = 14
os.environ['JINA_PARALLEL'] = str(1)
os.environ['JINA_SHARDS'] = str(1)
os.environ['JINA_TMP_DATA_DIR'] = '/tmp/jina/faiss/siftsmall'


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
    groundtruth_path = os.path.join(os.environ['JINA_TMP_DATA_DIR'], 'siftsmall_groundtruth.ivecs')
    groundtruth = ivecs_read(groundtruth_path)
    eval = (results[:, :k] == groundtruth[:, :1]).sum() / float(results.shape[0])
    return eval


@click.command()
@click.option('--task', '-t')
@click.option('--batch_size', '-n', default=50)
@click.option('--top_k', '-k', default=5)
def main(task, batch_size, top_k):
    if task == 'index':
        data_path = os.path.join(os.environ['JINA_TMP_DATA_DIR'], 'siftsmall_base.fvecs')
        with Flow.load_config('flow-index.yml') as flow:
            flow.index_ndarray(read_data(data_path), batch_size=batch_size)
    elif task == 'query':
        data_path = os.path.join(os.environ['JINA_TMP_DATA_DIR'], 'siftsmall_query.fvecs')
        with Flow.load_config('flow-query.yml') as flow:
            ppr = lambda x: save_topk(x, os.path.join(os.environ['JINA_TMP_DATA_DIR'], 'query_results.txt'), top_k)
            flow.search_ndarray(read_data(data_path), output_fn=ppr, top_k=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
