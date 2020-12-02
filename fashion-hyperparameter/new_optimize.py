import os

from fashion.data import get_data
from fashion.evaluation import index_document_generator, evaluation_document_generator

from optimize_class import FlowRunner, Optimizer

DATA_DIRECTORY = 'data'

def config_environment():
    #Todo: remove all env
    os.environ.setdefault('JINA_PARALLEL', '1')
    os.environ.setdefault('JINA_SHARDS', '1')
    os.environ.setdefault('JINA_LOG_CONFIG', 'logging.optimizer.yml')


def main():
    config_environment()
    data = get_data(DATA_DIRECTORY)
    flow_runner = FlowRunner(
                    index_document_generator(1000, data), evaluation_document_generator(1000, data),
                    500, 500,
                    overwrite_workspace=True)
    opt = Optimizer(flow_runner, 
                    'pods', 'flows/index.yml', 'flows/evaluate.yml', 'flows/parameter.yml',
                     2)
    opt.optimize_flow()


if __name__ == '__main__':
    main()
