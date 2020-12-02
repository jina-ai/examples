import os
from collections import defaultdict
from itertools import tee
import json
import shutil

from jina.flow import Flow
from jina.helper import colored
from jina.logging import default_logger as logger


class FlowRunner:
    def __init__(self, index_yaml, query_yaml, 
                       index_document_generator, query_document_generator,
                       index_batch_size, query_batch_size,
                       workspace_env_name = 'JINA_WORKSPACE', overwrite_workspace=False):

        self.index_yaml = index_yaml
        self.query_yaml = query_yaml
        self.index_document_generator = index_document_generator
        self.query_document_generator = query_document_generator
        self.index_batch_size = index_batch_size
        self.query_batch_size = query_batch_size
        self.workspace_env_name = workspace_env_name
        self.overwrite_workspace = overwrite_workspace

    def clean_workdir(self):
        if os.path.exists(os.environ[self.workspace_env_name]):
            shutil.rmtree(os.environ[self.workspace_env_name])
            logger.warning('Workspace deleted')

    def run_indexing(self):
        if os.path.exists(os.environ[self.workspace_env_name]):
            if self.overwrite_workspace:
                self.clean_workdir()
                print(colored('--------------------------------------------------------', 'red'))
                print(colored('-------------- Existing workspace deleted --------------', 'red'))
                print(colored('--------------------------------------------------------', 'red'))
            else:
                print(colored('--------------------------------------------------------', 'cyan'))
                print(colored('----- Workspace already exists. Skipping indexing. -----', 'cyan'))
                print(colored('--------------------------------------------------------', 'cyan'))
                return

        self.index_document_generator, index_document_generator_ = tee(self.index_document_generator)

        with Flow().load_config(self.index_yaml) as f:
            f.index(index_document_generator_, batch_size=self.index_batch_size)

    def run_querying(self, callback):
        self.query_document_generator, evaluation_document_generator_ = tee(self.query_document_generator)

        with Flow().load_config(self.query_yaml) as f:
            f.search(
                evaluation_document_generator_,
                batch_size=self.query_batch_size,
                output_fn=callback
            )

    @staticmethod
    def parameters_to_env(parameters):
        for environment_variable, value in parameters.items():
            os.environ[environment_variable] = str(value)

    def run_evaluation(self, parameters, evaluation_callback):
        FlowRunner.parameters_to_env(parameters)
        self.run_indexing()
        self.run_querying(evaluation_callback)


class Optimizer:
    def __init__(self, flow_runner,
                       trial_parameter_sampler,
                       n_trials,
                       direction='maximize', seed=42,
                       config_dir='config', best_config_filename='best_config.json'):
        self.flow_runner = flow_runner
        self.trial_parameter_sampler = trial_parameter_sampler
        self.n_trials = n_trials
        self.direction = direction
        self.seed = seed
        self.config_dir = config_dir
        self.best_config_filename = best_config_filename

    def objective(self, trial):
        parameters = self.trial_parameter_sampler(trial)
        cb = OptimizerCallback()
        self.flow_runner.run_evaluation(parameters, cb.process_result)
        evaluation_values = cb.get_mean_evaluation()
        op_name = list(evaluation_values)[0]
        mean_eval = evaluation_values[op_name]
        logger.info(colored(f'Avg {op_name}: {mean_eval}', 'green'))
        return mean_eval

    def export_params(self, study):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(f'{self.config_dir}/{self.best_config_filename}', 'w') as f: json.dump(study.best_trial.params, f)
        logger.info(colored(f'Number of finished trials: {len(study.trials)}', 'green'))
        logger.info(colored(f'Best trial: {study.best_trial.params}', 'green'))
        logger.info(colored(f'Time to finish: {study.best_trial.duration}', 'green'))

    def optimize_flow(self):
        import optuna
        sampler = optuna.samplers.TPESampler(seed=self.seed)
        study = optuna.create_study(direction=self.direction, sampler=sampler)
        study.optimize(self.objective, n_trials=self.n_trials)
        self.export_params(study)


class OptimizerCallback:
    def __init__(self):
        self.evaluation_values = {}
        self.n_docs = 0

    def get_mean_evaluation(self, op_name=None):
        if op_name:
            return self.evaluation_values[op_name] / self.n_docs
        return {metric: val / self.n_docs for metric, val in self.evaluation_values.items()}

    def process_result(self, response):
        self.n_docs += len(response.search.docs)
        logger.info(f'>> Num of docs: {self.n_docs}')
        for doc in response.search.docs:
            for evaluation in doc.evaluations:
                self.evaluation_values[evaluation.op_name] = self.evaluation_values.get(evaluation.op_name, 0.0) + evaluation.value
                
