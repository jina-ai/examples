import os

from fashion.data import get_data
from fashion.evaluation import index_document_generator, evaluation_document_generator

from optimize_class import FlowRunner, Optimizer

DATA_DIRECTORY = 'data'

def main():
    data = get_data(DATA_DIRECTORY)
    flow_runner = FlowRunner(
                    index_document_generator(1000, data), evaluation_document_generator(1000, data),
                    500, 500,
                    env_yaml='flows/env.yml',
                    overwrite_workspace=False)
    opt = Optimizer(flow_runner, 
                    'pods', 'flows/index.yml', 'flows/evaluate.yml', 'flows/parameter.yml')
    opt.optimize_flow(n_trials=2)


if __name__ == '__main__':
    main()
