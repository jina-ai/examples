__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import Generator, Any

import click
import os
import string
import random
import numpy as np

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


def fvecs_read(filename: str, c_contiguous: bool = True) -> np.ndarray:
    fv = np.fromfile(filename, dtype=np.float32)
    if fv.size == 0:
        return np.zeros((0, 0))
    dim = fv.view(np.int32)[0]
    assert dim > 0
    fv = fv.reshape(-1, 1 + dim)
    if not all(fv.view(np.int32)[:, 0] == dim):
        raise IOError("Non-uniform vector sizes in " + filename)
    fv = fv[:, 1:]
    if c_contiguous:
        fv = fv.copy()
    return fv


def read_data(db_file_path: str, max_sample_size: int = -1) -> Generator[bytes, Any, Any]:
    vectors = fvecs_read(db_file_path)
    num_vectors = vectors.shape[0]
    batch_size = 1 if max_sample_size == -1 else max_sample_size
    num_batches = int(num_vectors / batch_size)
    for i in range(1, num_batches + 1):
        start_batch = (i - 1) * batch_size
        end_batch = i * batch_size if i * batch_size < num_vectors else num_vectors
        #print(vectors[start_batch: end_batch])
        #print(vectors[start_batch: end_batch].shape)
        yield vectors[start_batch: end_batch].tobytes()


def save_topk(resp, output_fn=None):
    results = []
    for d in resp.search.docs:
        cur_result = []
        d_fn = d.meta_info.decode()
        cur_result.append(d_fn)
        print("-" * 20)
        print(f'query vector: {d_fn}')
        print('matched vectors' + "*" * 10)
        print("{}".format(d.buffer.decode()))
        for idx, kk in enumerate(d.topk_results):
            score = kk.score.value
            if score < 0.0:
                continue
            m_fn = kk.match_doc.buffer.decode()
            print('{:>2d}:({:f}):{}'.format(
                idx, score, m_fn))
            cur_result.append(m_fn)
        results.append(cur_result)


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
@click.option('--top_k', '-k', default=5)
# @click.option('--path', '-p', help='Specify a JPG file or directory to query', default='')
def main(task, num_docs, top_k):
    os.environ['TMP_WORKSPACE'] = get_random_ws(os.environ['TMP_DATA_DIR'])
    if task == 'index':
        print("HEY")
        data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'siftsmall_base.fvecs')
        #print("HEY " + data_path)
        #gen = read_data(data_path, num_docs)
        #buf = next(gen)
        #bytes_length = len(buf)
        #data_size_bytes = 4
        #array_length = int(bytes_length / data_size_bytes)
        #print("Bytes length " + str(bytes_length) + " array_length " + str(array_length))
        #print(np.frombuffer(buf, dtype='float32'))
        #print(np.frombuffer(buf, dtype='float32').reshape(2, 128))
        #buf = next(gen)
        #print(np.frombuffer(buf, dtype='float32').reshape(2, 128))
        #buf = next(gen)
        #print(np.frombuffer(buf, dtype='float32').reshape(2, 128))
        #buf = next(gen)
        #print(np.frombuffer(buf, dtype='float32').reshape(2, 128))
        #buf = next(gen)
        #print(np.frombuffer(buf, dtype='float32').reshape(2, 128))
        #buf = next(gen)
        #print(np.frombuffer(buf, dtype='float32').reshape(2, 128))
        flow = Flow().load_config('flow-index.yml')
        with flow.build() as fl:
            fl.index(read_data(data_path, num_docs), batch_size=num_docs)
    elif task == 'query':
        data_path = os.path.join(os.environ['TMP_DATA_DIR'], 'siftsmall_query.fvecs')
        flow = Flow().load_config('flow-query.yml')
        with flow.build() as fl:
            ppr = lambda x: save_topk(x, os.path.join(os.environ['TMP_DATA_DIR'], 'query_results.txt'))
            fl.search(buffer=read_data(data_path, 5), callback=ppr, top_k=top_k)
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
