__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import click
import os

from collections import defaultdict
from functools import partial

from jina.flow import Flow
from jina import Document

from read_vectors_files import fvecs_read, ivecs_read


def config(indexer_query_type: str):
    os.environ['JINA_PARALLEL'] = str(1)
    os.environ['JINA_SHARDS'] = str(1)
    os.environ['JINA_TMP_DATA_DIR'] = os.environ.get('JINA_TMP_DATA_DIR', './siftsmall')
    if indexer_query_type == 'faiss':
        os.environ['JINA_USES'] = os.environ.get('JINA_USES_FAISS',
                                                 'docker://jinahub/pod.indexer.faissindexer:0.0.12-0.9.3')
        os.environ['JINA_USES_INTERNAL'] = 'yaml/faiss-indexer.yml'
    elif indexer_query_type == 'annoy':
        os.environ['JINA_USES'] = os.environ.get('JINA_USES_ANNOY',
                                                 'docker://jinahub/pod.indexer.annoyindexer:0.0.13-0.9.3')
        os.environ['JINA_USES_INTERNAL'] = 'yaml/annoy-indexer.yml'
    elif indexer_query_type == 'numpy':
        os.environ['JINA_USES'] = 'yaml/indexer.yml'


def index_generator(db_file_path: str):
    documents = fvecs_read(db_file_path)
    for id, data in enumerate(documents):
        with Document() as doc:
            doc.content = data
            doc.tags['id'] = id
        yield doc


def evaluate_generator(db_file_path: str, groundtruth_path: str):
    documents = fvecs_read(db_file_path)
    groundtruths = ivecs_read(groundtruth_path)

    for data_doc, gt_indexes in zip(documents, groundtruths):
        with Document() as doc:
            doc.content = data_doc
        with Document() as groundtruth:
            for index in gt_indexes:
                with Document() as match:
                    match.tags['id'] = int(index.item())
                groundtruth.matches.add(match)

        yield doc, groundtruth


def run(task, batch_size, top_k, indexer_query_type):
    config(indexer_query_type)

    if task == 'index':
        data_path = os.path.join(os.environ['JINA_TMP_DATA_DIR'], 'siftsmall_base.fvecs')
        with Flow.load_config('flow-index.yml') as flow:
            flow.index(index_generator(data_path), batch_size=batch_size)
    elif task == 'query':
        evaluation_results = defaultdict(float)

        def _get_evaluation_results(evaluation_results: dict, resp):
            for d in resp.search.docs:
                for eval in d.evaluations:
                    evaluation_results[eval.op_name] = eval.value

        get_evaluation_results = partial(_get_evaluation_results, evaluation_results)

        data_path = os.path.join(os.environ['JINA_TMP_DATA_DIR'], 'siftsmall_query.fvecs')
        groundtruth_path = os.path.join(os.environ['JINA_TMP_DATA_DIR'], 'siftsmall_groundtruth.ivecs')
        with Flow.load_config('flow-query.yml') as flow:
            flow.search(evaluate_generator(data_path, groundtruth_path), output_fn=get_evaluation_results,
                        top_k=top_k)
        print(f' RESULTS {evaluation_results}')
        evaluation = evaluation_results['RecallEvaluator']
        print(f' Recall@{top_k} => {100*evaluation}%')
        # return for test
        return 100*evaluation
    else:
        raise NotImplementedError(
            f'unknown task: {task}. A valid task is either `index` or `query`.')


@click.command()
@click.option('--task', '-t')
@click.option('--batch_size', '-n', default=50)
@click.option('--top_k', '-k', default=100)
@click.option('--indexer-query-type', '-i', type=click.Choice(['faiss', 'annoy', 'numpy'], case_sensitive=False),
              default='faiss')
def main(task, batch_size, top_k, indexer_query_type):
    run(task, batch_size, top_k, indexer_query_type)


if __name__ == '__main__':
    main()
