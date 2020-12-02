import os

from fashion.config import get_run_parameters
from fashion.data import get_data
from fashion.evaluation import run_evaluation


DATA_DIRECTORY = 'data'

class Callback:
    def __init__(self):
        self.evaluation_values = {}
        self.n_docs = 0

    def get_mean_evaluation(self, op_name=None):
        if op_name:
            return self.evaluation_values[op_name] / self.n_docs
        return {metric: val / self.n_docs for metric, val in self.evaluation_values.items()}

    def process_result(self, response):
        self.n_docs = len(response.search.docs)
        print(f'>> Num of docs: {self.n_docs}')
        for doc, groundtruth in zip(response.search.docs, response.search.groundtruths):
            for evaluation in doc.evaluations:
                print(evaluation.op_name, evaluation.value)
                self.evaluation_values[evaluation.op_name] = self.evaluation_values.get(evaluation.op_name, 0.0) + evaluation.value


def config_environment():
    os.environ.setdefault('JINA_DATA_DIRECTORY', 'data')


def sample_run_parameters(trial):
    target_dimension = trial.suggest_int('target_dimension', 32, 256, step=32)
    return get_run_parameters(target_dimension)


def optimize_target_dimension(data, trial):
    parameters = sample_run_parameters(trial)
    cb = Callback()
    run_evaluation(data, parameters, cb.process_result)
    evaluation_values = cb.get_mean_evaluation()
    op_name = list(evaluation_values)[0]
    mean_eval = evaluation_values[op_name]
    print(f'Avg {op_name}: {mean_eval}')
    return mean_eval


def execute_trial(trial):
    data = get_data(DATA_DIRECTORY)
    return optimize_target_dimension(data, trial)


def main():
    config_environment()
    import optuna
    sampler = optuna.samplers.TPESampler(seed=42)
    study = optuna.create_study(direction='maximize', sampler=sampler)
    study.optimize(execute_trial, n_trials=5)
    print('Number of finished trials:', len(study.trials))
    print('Best trial:', study.best_trial.params)
    print('Time to finish:', study.best_trial.duration)


if __name__ == '__main__':
    main()
