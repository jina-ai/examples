__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
import click
import random
from jina import Flow, Document, DocumentArray
from jina.logging.predefined import default_logger as logger

MAX_DOCS = int(os.environ.get('JINA_MAX_DOCS', 10000))


def config(dataset: str):
    if dataset == 'toy':
        os.environ['JINA_DATA_FILE'] = os.environ.get('JINA_DATA_FILE', 'data/toy-input.txt')
    elif dataset == 'full':
        os.environ['JINA_DATA_FILE'] = os.environ.get('JINA_DATA_FILE', 'data/input.txt')
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(45678))
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ.setdefault('JINA_WORKSPACE', os.path.join(cur_dir, 'workspace'))
    os.environ.setdefault('JINA_WORKSPACE_MOUNT',
                          f'{os.environ.get("JINA_WORKSPACE")}:/workspace/workspace')


def print_topk(resp, sentence):
    for doc in resp.data.docs:
        print(f"\n\n\nTa-Dah🔮, here's what we found for: {sentence}")
        for idx, match in enumerate(doc.matches):
            score = match.scores['cosine'].value
            print(f'> {idx:>2d}({score:.2f}). {match.text}')


def input_generator(num_docs: int, file_path: str):
    with open(file_path) as file:
        lines = file.readlines()
    num_lines = len(lines)
    random.shuffle(lines)
    for i in range(min(num_docs, num_lines)):
        yield Document(text=lines[i])


def index(num_docs):
    flow = Flow().load_config('flows/flow.yml')
    data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None))
    with flow:
        flow.post(on='/index', inputs=input_generator(num_docs, data_path),
                  show_progress=True)


def query(top_k):
    flow = Flow().load_config('flows/flow.yml')
    with flow:
        text = input('Please type a sentence: ')
        doc = Document(content=text)

        result = flow.post(on='/search', inputs=DocumentArray([doc]),
                           parameters={'top_k': top_k},
                           line_format='text',
                           return_results=True,
                           )
        print_topk(result[0], text)


@click.command()
@click.option(
    '--task',
    '-t',
    type=click.Choice(['index', 'query'], case_sensitive=False),
)
@click.option('--num_docs', '-n', default=MAX_DOCS)
@click.option('--top_k', '-k', default=5)
@click.option('--dataset', '-d', type=click.Choice(['toy', 'full']), default='toy')
def main(task, num_docs, top_k, dataset):
    config(dataset)
    if task == 'index':
        if os.path.exists(os.environ.get("JINA_WORKSPACE")):
            logger.error(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {os.environ.get("JINA_WORKSPACE")} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
            sys.exit(1)
        index(num_docs)
    elif task == 'query':
        query(top_k)


if __name__ == '__main__':
    main()
