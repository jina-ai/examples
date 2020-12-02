import os
from collections import defaultdict
from fashion.data import get_data
from fashion.evaluation import run_evaluation
from fashion.config import get_run_parameters

from jina.helper import colored


def print_evaluation_results(response):
    evaluation_values = defaultdict(list)
    for doc in response.search.docs:
        for evaluation in doc.evaluations:
            evaluation_values[evaluation.op_name].append(evaluation.value)
    for name, values in evaluation_values.items():
        average_score = sum(values) / len(values)
        result_string = f'Average score for {name}: {average_score}'
        length = len(result_string)
        print(colored('-' * (length + 12), 'cyan'))
        print(colored('-----', 'cyan'), colored(result_string, "green"), colored('-----', 'cyan'))
        print(colored('-' * (length + 12), 'cyan'))


def config_global_environment():
    os.environ.setdefault('JINA_DATA_DIRECTORY', 'data')
    os.environ.setdefault('JINA_LOG_CONFIG', 'logging.yml')


def main():
    config_global_environment()
    data = get_data()
    parameters = get_run_parameters(64)
    run_evaluation(data, parameters, print_evaluation_results)


if __name__ == '__main__':
    main()
