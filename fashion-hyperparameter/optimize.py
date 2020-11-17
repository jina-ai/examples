import csv
import os

from pathlib import Path

from jina.flow import Flow
from jina.helloworld.helper import download_data
from jina.proto import jina_pb2


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


TEST_PARAMETERS = {
    'JINA_INDEX_DATA_FILE': 'tests/hyperparameter/index_data.csv',
    'JINA_EVALUATION_DATA_FILE': 'tests/hyperparameter/query_data.csv',
    'JINA_WORKSPACE': 'workspace_eval',
}


def run_evaluation(targets, parameters, callback):
    for environment_variable, value in parameters.items():
        os.environ[environment_variable] = str(value)
    run_indexing('flows/index.yml', targets)
    run_querying('flows/query.yml', callback)


def index_document_generator(num_doc, target):
    for j in range(num_doc):
        label_int = target['index-labels']['data'][j][0]
        d = jina_pb2.Document()
        d.blob.CopyFrom((target['index']['data'][j]))
        d.tags.update({'label_id': label_int})
        yield d


def get_index_document_iterator(index_filename):
    with open(index_filename, 'r') as index_file:
        for doc_id, row in enumerate(index_file.readlines()):
            next_doc = jina_pb2.Document()
            next_doc.tags['id'] = str(doc_id)
            next_doc.text = row
            yield next_doc


def run_indexing(flow_file, targets):
    if os.path.exists(os.environ['JINA_WORKSPACE']):
        print('--------------------------------------------------------')
        print('----- Workspace already exists. Skipping indexing. -----')
        print('--------------------------------------------------------')
    else:
        with Flow().load_config(flow_file) as f:
            f.index(index_document_generator(4096, targets), batch_size=2048)


def process_result(response):
    # pass
    for doc in response.docs:
        print(doc.text)
        print([(match.text, match.tags['id']) for match in doc.matches])
        for evaluation in doc.evaluations:

            print(evaluation.op_name, evaluation.value)

    # for doc in response.docs:
    #     print(doc.text)
    # print(response)


def get_evaluation_document_iterator(evaluation_filename):
    with open(evaluation_filename, 'r') as evaluation_file:
        evaluation_reader = csv.reader(evaluation_file)
        for row in evaluation_reader:
            next_doc = jina_pb2.Document()
            next_doc.text = row[1]
            groundtruth_doc = jina_pb2.Document()
            for match_id in row[0].split(' '):
                match = groundtruth_doc.matches.add()
                match.tags['id'] = match_id
            yield next_doc, groundtruth_doc


def run_querying(flow_file, callback):
    with Flow().load_config(flow_file) as evaluation_flow:
        evaluation_flow.search(
            get_evaluation_document_iterator(os.environ['JINA_EVALUATION_DATA_FILE']),
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
    os.environ.setdefault('JINA_WORKSPACE', 'workspace_eval')


def main():
    # target = Target('localhost', 8000, 'http')
    # delete_flow(target, 'ccbe20d2-1ef3-4afe-b4cd-af2ef04ff648')
    workspace = os.environ['JINA_WORKSPACE']
    Path(workspace).mkdir(parents=True, exist_ok=True)

    targets = {
        'index-labels': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-labels-idx1-ubyte.gz',
            'filename': os.path.join(workspace, 'index-labels'),
        },
        'query-labels': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-labels-idx1-ubyte.gz',
            'filename': os.path.join(workspace, 'query-labels'),
        },
        'index': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/train-images-idx3-ubyte.gz',
            'filename': os.path.join(workspace, 'index'),
        },
        'query': {
            'url': 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/t10k-images-idx3-ubyte.gz',
            'filename': os.path.join(workspace, 'query'),
        },
    }

    download_data(targets)

    run_evaluation(TEST_PARAMETERS, process_result)


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
