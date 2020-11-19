import csv
import os

from jina.flow import Flow
from jina.proto import jina_pb2
from jina.types.ndarray.generic import NdArray

from pods.components import MyEncoder
from pods.evaluate import MyEvaluator
from optimization.data import get_data


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


def config_environment():
    os.environ.setdefault('JINA_DATA_DIRECTORY', 'data')
    os.environ.setdefault('JINA_PARALLEL', '1')
    os.environ.setdefault('JINA_SHARDS', '1')


def get_run_parameters(trial):
    target_dimension = trial.suggest_int('target_dimension', 32, 256, step=32)
    return {
        'JINA_INDEX_DATA_FILE': 'tests/hyperparameter/index_data.csv',
        'JINA_EVALUATION_DATA_FILE': 'tests/hyperparameter/query_data.csv',
        'JINA_WORKSPACE': f'workspace_eval_{target_dimension}',
        'JINA_TARGET_DIMENSION': f'{target_dimension}'
    }


def optimize_target_dimension(data, trial):
    parameters = get_run_parameters(trial)
    cb = Callback()
    run_evaluation(data, parameters, cb.process_result)
    evaluation_values = cb.get_mean_evaluation()
    op_name = list(evaluation_values)[0]
    mean_eval = evaluation_values[op_name]
    print(f'Avg {op_name}: {mean_eval}')
    return mean_eval


def main(trial):
    config_environment()
    data = get_data()
    return optimize_target_dimension(data, trial)


if __name__ == '__main__':
    import optuna
    study = optuna.create_study(direction='maximize')
    study.optimize(main, n_trials=5)
    print('Number of finished trials:', len(study.trials))
    print('Best trial:', study.best_trial.params)