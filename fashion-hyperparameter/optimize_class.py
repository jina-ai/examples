import os
from collections import defaultdict
from itertools import tee
import json
from pathlib import Path
import shutil

from ruamel.yaml import YAML

from jina.flow import Flow
from jina.helper import colored
from jina.logging import default_logger as logger


class FlowRunner:
    def __init__(self, index_document_generator, query_document_generator,
                       index_batch_size, query_batch_size,
                       workspace_env_name = 'JINA_WORKSPACE', 
                       workspace=None, overwrite_workspace=False):

        self.index_document_generator = index_document_generator
        self.query_document_generator = query_document_generator
        self.index_batch_size = index_batch_size
        self.query_batch_size = query_batch_size
        self.workspace_env_name = workspace_env_name
        self.overwrite_workspace = overwrite_workspace

    def clean_workdir(self, workspace):
        if Path(workspace).exists():
            shutil.rmtree(workspace)
            logger.warning('Workspace deleted')

    def run_indexing(self, index_yaml, workspace=None):
        workspace = os.environ.get(self.workspace_env_name, workspace)

        if Path(workspace).exists():
            if self.overwrite_workspace:
                self.clean_workdir(workspace)
                print(colored('--------------------------------------------------------', 'red'))
                print(colored('-------------- Existing workspace deleted --------------', 'red'))
                print(colored('--------------------------------------------------------', 'red'))
            else:
                print(colored('--------------------------------------------------------', 'cyan'))
                print(colored('----- Workspace already exists. Skipping indexing. -----', 'cyan'))
                print(colored('--------------------------------------------------------', 'cyan'))
                return

        self.index_document_generator, index_document_generator = tee(self.index_document_generator)

        with Flow().load_config(index_yaml) as f:
            f.index(index_document_generator, batch_size=self.index_batch_size)

    def run_querying(self, query_yaml, callback, workspace=None):
        self.query_document_generator, query_document_generator = tee(self.query_document_generator)

        with Flow().load_config(query_yaml) as f:
            f.search(
                query_document_generator,
                batch_size=self.query_batch_size,
                output_fn=callback
            )

    @staticmethod
    def parameters_to_env(parameters):
        for environment_variable, value in parameters.items():
            os.environ[environment_variable] = str(value)

    def run_evaluation(self, index_yaml, query_yaml, workspace, evaluation_callback):
        self.run_indexing(index_yaml, workspace)
        self.run_querying(query_yaml, evaluation_callback, workspace)


class Optimizer:
    def __init__(self, flow_runner, pod_dir,
                       index_yaml, query_yaml, parameter_yaml,
                       n_trials, direction='maximize', seed=42,
                       config_dir='config', best_config_filename='best_config.json',
                       overwrite_trial_workspace=True):
        self.flow_runner = flow_runner
        self.pod_dir = Path(pod_dir)
        self.index_yaml = Path(index_yaml)
        self.query_yaml = Path(query_yaml)
        self.parameter_yaml = parameter_yaml
        self.n_trials = n_trials
        self.direction = direction
        self.seed = seed
        self.config_dir = config_dir
        self.best_config_filename = best_config_filename
        self.overwrite_trial_workspace = overwrite_trial_workspace

    def _trial_parameter_sampler(self, trial):
        """ https://optuna.readthedocs.io/en/stable/reference/generated/optuna.trial.Trial.html#optuna.trial.Trial
        """
        param_dict = {}
        yaml = YAML(typ='safe')
        parameters = yaml.load(open(self.parameter_yaml))
        for param, param_values in parameters.items():
            kwargs = {}
            for kwarg in param_values: 
                kwargs = {**kwargs, **kwarg}
            param_type = 'suggest_' + kwargs['type']
            del kwargs['type']
            param_dict[param] = getattr(trial, param_type)(param, **kwargs)
        return param_dict

    @staticmethod
    def _replace_param(parameters, trial_parameters):
        for section in ['with', 'metas']:
            if section in parameters:
                for param, val in parameters[section].items():
                    val = str(val).lstrip('$')
                    if val in trial_parameters:
                        parameters[section][param] = trial_parameters[val]
        return parameters

    def _create_trial_pods(self, trial_dir, trial_parameters):
        trial_pod_dir = trial_dir/'pods'
        shutil.copytree(self.pod_dir, trial_pod_dir)
        yaml=YAML(typ='rt')
        for file_path in self.pod_dir.glob('*.yml'):
            parameters = yaml.load(file_path)
            if 'components' in parameters:
                for i, component in enumerate(parameters['components']):
                    parameters['components'][i] = Optimizer._replace_param(component, trial_parameters)
            parameters = Optimizer._replace_param(parameters, trial_parameters)
            new_pod_file_path = trial_pod_dir/file_path.name
            yaml.dump(parameters, open(new_pod_file_path, 'w'))

    def _create_trial_flows(self, trial_dir):
        trial_flow_dir = trial_dir/'flows'
        trial_flow_dir.mkdir(exist_ok=True)
        yaml=YAML(typ='rt')
        for file_path in [self.index_yaml, self.query_yaml]:
            parameters = yaml.load(file_path)
            for pod, val in parameters['pods'].items():
                for pod_param, pod_arg in parameters['pods'][pod].items():
                    if pod_param.startswith('uses'):
                        parameters['pods'][pod][pod_param] = str(trial_dir/self.pod_dir/Path(val[pod_param]).name)
            trial_flow_file_path = trial_flow_dir/file_path.name
            yaml.dump(parameters, open(trial_flow_file_path, 'w'))

    def _objective(self, trial):
        trial_parameters = self._trial_parameter_sampler(trial)
        trial_workspace = Path('JINA_WORKSPACE_' + '_'.join([str(v) for v in trial_parameters.values()]))
        trial_parameters['JINA_WORKSPACE'] = str(trial_workspace)
        trial_index_workspace = trial_workspace/'index'
        trial_index_yaml = trial_workspace/'flows'/self.index_yaml.name
        trial_query_yaml = trial_workspace/'flows'/self.query_yaml.name

        if trial_workspace.exists() and self.overwrite_trial_workspace:
            shutil.rmtree(trial_workspace)
            print(colored('--------------------------------------------------------', 'red'))
            print(colored('---------- Existing trial workspace deleted ------------', 'red'))
            print(colored('--------------------------------------------------------', 'red'))
            print(colored('WORKSPACE: ' + str(trial_workspace), 'red'))
        self._create_trial_pods(trial_workspace, trial_parameters)
        self._create_trial_flows(trial_workspace)
        cb = OptimizerCallback()
        self.flow_runner.run_evaluation(trial_index_yaml, trial_query_yaml, trial_index_workspace, cb.process_result)

        evaluation_values = cb.get_mean_evaluation()
        op_name = list(evaluation_values)[0]
        mean_eval = evaluation_values[op_name]
        logger.info(colored(f'Avg {op_name}: {mean_eval}', 'green'))
        return mean_eval

    def _export_params(self, study):
        Path(self.config_dir).mkdir(exist_ok=True)
        with open(f'{self.config_dir}/{self.best_config_filename}', 'w') as f: json.dump(study.best_trial.params, f)
        logger.info(colored(f'Number of finished trials: {len(study.trials)}', 'green'))
        logger.info(colored(f'Best trial: {study.best_trial.params}', 'green'))
        logger.info(colored(f'Time to finish: {study.best_trial.duration}', 'green'))

    def optimize_flow(self):
        import optuna
        sampler = optuna.samplers.TPESampler(seed=self.seed)
        study = optuna.create_study(direction=self.direction, sampler=sampler)
        study.optimize(self._objective, n_trials=self.n_trials)
        self._export_params(study)


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
                
