import os

from jina.flow import Flow
from jina.proto import jina_pb2
from jina.types.ndarray.generic import NdArray

from pods.components import MyEncoder
from pods.evaluate import MyEvaluator


def run_evaluation(targets, parameters, callback):
    for environment_variable, value in parameters.items():
        os.environ[environment_variable] = str(value)
    run_indexing('flows/index.yml', targets)
    run_querying('flows/evaluate.yml', targets, callback)


def index_document_generator(num_doc, target):
    for j in range(num_doc):
        label_int = target['index-labels']['data'][j][0]
        d = jina_pb2.DocumentProto()
        NdArray(d.blob).value = target['index']['data'][j]
        d.tags['label_id'] = str(label_int)
        yield d


def run_indexing(flow_file, targets):
    if os.path.exists(os.environ['JINA_WORKSPACE']):
        print('--------------------------------------------------------')
        print('----- Workspace already exists. Skipping indexing. -----')
        print('--------------------------------------------------------')
        return

    with Flow().load_config(flow_file) as f:
        f.index(index_document_generator(60000, targets), batch_size=2048)


def evaluation_document_generator(num_doc, target):
    for j in range(num_doc):
        label_int = target['query-labels']['data'][j][0]
        next_doc = jina_pb2.DocumentProto()
        NdArray(next_doc.blob).value = target['query']['data'][j]

        groundtruth_doc = jina_pb2.DocumentProto()
        m1 = groundtruth_doc.matches.add()
        m1.tags['label_id'] = str(label_int)

        yield next_doc, groundtruth_doc


def run_querying(flow_file, targets, callback):
    with Flow().load_config(flow_file) as evaluation_flow:
        evaluation_flow.search(
            evaluation_document_generator(100, targets),
            output_fn=callback,
            callback_on_body=True,
        )
