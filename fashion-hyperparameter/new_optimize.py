import os

from fashion.config import get_run_parameters
from fashion.data import get_data
from fashion.evaluation import index_document_generator, evaluation_document_generator

# from jina.optimize import Optimizer
from optimize_class import Optimizer



def config_environment():
    os.environ.setdefault('JINA_DATA_DIRECTORY', 'data')


def sample_run_parameters(trial):
    target_dimension = trial.suggest_int('target_dimension', 32, 256, step=32)
    return get_run_parameters(target_dimension)


def main():
    config_environment()
    data = get_data()
    opt = Optimizer('flows/index.yml', 'flows/evaluate.yml',
                    index_document_generator(1000, data), evaluation_document_generator(1000, data),
                    500, 500,
                    sample_run_parameters, 
                    5)
    opt.optimize_flow()


if __name__ == '__main__':
    main()
