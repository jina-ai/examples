import csv
import os

from jina.flow import Flow
from jina.proto import jina_pb2
from jina.types.ndarray.generic import NdArray

from pods.components import MyEncoder
from pods.evaluate import MyEvaluator
from optimization.data import get_data


class Hyperoptimizer:
    def __init__(self):
        self.parameters = [
            {
                'JINA_INDEX_DATA_FILE': 'tests/hyperparameter/index_data.csv',
                'JINA_EVALUATION_DATA_FILE': 'tests/hyperparameter/query_data.csv',
                'JINA_WORKSPACE': 'workspace_eval',
                'JINA_MATRIX_SIZE': size,
            }
            for size in range(10, 100)
        ]

    def parameters_iterator(self):
        yield {}, self.save_results

    def save_results(self, results):
        pass


def run_evaluation(targets, parameters, callback):
    for environment_variable, value in parameters.items():
        os.environ[environment_variable] = str(value)
    run_indexing('flows/index.yml', targets)
    run_querying('flows/query.yml', targets, callback)


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

class Callback:
    def __init__(self):
        self.evaluation_values = {}
        self.n_docs = 0
    
    def get_mean_evaluation(self, op_name=None):
        if op_name:
            return self.evaluation_values[op_name]/self.n_docs
        return {metric:val/self.n_docs for metric, val in self.evaluation_values.items()}

    def process_result(self, response):
        self.n_docs = len(response.search.docs)
        print(f'>> Num of docs: {self.n_docs}')
        for doc, groundtruth in zip(response.search.docs, response.search.groundtruths):
            for evaluation in doc.evaluations: 
                # print(evaluation.op_name, evaluation.value)
                # print(evaluation)
                self.evaluation_values[evaluation.op_name] = self.evaluation_values.get(evaluation.op_name, 0.0) + evaluation.value

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


def optimize():
    optimizer = Hyperoptimizer()

    for parameters, callback in optimizer.iterate():
        run_indexing(parameters)
        values = run_evaluation(parameters)
        callback(values)

    return optimizer


def config_environment():
    os.environ.setdefault('JINA_DATA_DIRECTORY', 'data')
    os.environ.setdefault('JINA_PARALLEL', '1')
    os.environ.setdefault('JINA_SHARDS', '1')


def get_run_parameters(target_dimension):
    return {
        'JINA_INDEX_DATA_FILE': 'tests/hyperparameter/index_data.csv',
        'JINA_EVALUATION_DATA_FILE': 'tests/hyperparameter/query_data.csv',
        'JINA_WORKSPACE': f'workspace_eval_{target_dimension}',
        'JINA_TARGET_DIMENSION': f'{target_dimension}'
    }


def optimize_target_dimension(data):

    # optimizer = Hyperoptimizer(setup_parameters)
    # for parameterset, callback in optimizer.get_parameters():
    #     run_evaluation(data, parameters, callback)

    for i in range(64, 65):
        cb = Callback()
        parameters = get_run_parameters(i)
        run_evaluation(data, parameters, cb.process_result)
        evaluation_values = cb.get_mean_evaluation()
        op_name = list(evaluation_values)[0]
        mean_eval = evaluation_values[op_name]
        print(f'Avg {op_name}: {mean_eval}')


def main():
    # target = Target('localhost', 8000, 'http')
    # delete_flow(target, 'ccbe20d2-1ef3-4afe-b4cd-af2ef04ff648')
    config_environment()

    data = get_data()

    optimize_target_dimension(data)


if __name__ == '__main__':
    main()


# @dataclass
# class Target:
#     host: str = None
#     port: int = None
#     protocoll: str = 'http'

#     @property
#     def prefix(self):
#         return f"{self.protocoll}://{self.host}:{self.port}"


# def delete_flow(target, flow_id):
#     response = requests.delete(f'{target.prefix}/v1/flow?flow_id={flow_id}')
#     print(response.json())

# def run_remote_indexing(target):
#     flow_files = [
#         ('uses_files', ('pods/encode.yml', open('pods/encode.yml', 'rb'))),
#         ('uses_files', ('pods/extract.yml', open('pods/extract.yml', 'rb'))),
#         ('uses_files', ('pods/index.yml', open('pods/index.yml', 'rb'))),
#         ('pymodules_files', ('pods/text_loader.py', open('pods/text_loader.py', 'rb'))),
#         (
#             'yamlspec',
#             (
#                 'tests/hyperparameter/flow-index.yml',
#                 open('tests/hyperparameter/flow-index.yml', 'rb'),
#             ),
#         ),
#     ]

#     response_json = requests.put(
#         f'{target.prefix}/v1/flow/yaml', files=flow_files
#     ).json()
#     print(response_json)
#     # {'status_code': 200, 'flow_id': '6203e1af-67ed-46cd-a514-eae7d2d760a3', 'host': '0.0.0.0', 'port': 45678, 'status': 'started'}
#     if response_json['status_code'] != 200:
#         raise Exception(f"Could not start a flow with error: {response_json}")
#     # flow_id = response_json['flow_id']
#     for batch in get_data_batches():
#         requests.post('http://localhost:45678/api/index', json={'data': batch})

#     delete_flow(target, response_json['flow_id'])


# # curl --request POST -d '{"top_k": 10, "data": ["text:hey, dude"]}' -H 'Content-Type: application/json' '0.0.0.0:45678/api/search' | \
# #     jq -e ".search.docs[] | .matches[] | .text"


# # RUN bash get_data.sh ./data && \
# #     python app.py -t index && \
# #     rm -rf data

# #     -H  "accept: application/json" \
# #     -H  "Content-Type: multipart/form-data" \
