import os

from fashion.config import get_run_parameters
from fashion.data import get_data
from fashion.evaluation import index_document_generator, evaluation_document_generator

from optimize_class import FlowRunner, Optimizer


def config_environment():
    os.environ.setdefault('JINA_DATA_DIRECTORY', 'data')
    os.environ.setdefault('JINA_LOG_CONFIG', 'logging.optimizer.yml')


def trial_parameter_sampler(trial):
    target_dimension = trial.suggest_int('target_dimension', 32, 256, step=32)
    return get_run_parameters(target_dimension)


def main():
    config_environment()
    data = get_data()
    flow_runner = FlowRunner('flows/index.yml', 'flows/evaluate.yml',
                    index_document_generator(1000, data), evaluation_document_generator(1000, data),
                    500, 500,
                    overwrite_workspace=True)
    opt = Optimizer(flow_runner, trial_parameter_sampler, 3)
    opt.optimize_flow()


if __name__ == '__main__':
    main()
