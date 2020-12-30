__version__ = '0.0.1'

import os
import sys
from collections import defaultdict

from jina.flow import Flow
from jina import Document
from jina.types.score import NamedScore

evaluation_value = defaultdict(float)
num_evaluation_docs = 0
num_docs = int(os.environ.get('MAX_DOCS', 10))


def config():
    parallel = 1 if sys.argv[1] == 'index' else 1
    shards = 1

    os.environ['JINA_PARALLEL'] = str(parallel)
    os.environ['JINA_SHARDS'] = str(shards)
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))
    os.environ['JINA_DATA_PATH'] = 'dataset/test_answers.csv'


def index_generator():
    """
    Define data as Document to be indexed.
    """
    import csv
    data_path = os.path.join(os.path.dirname(__file__), os.environ['JINA_DATA_PATH'])

    # Get Document and ID
    with open(data_path) as f:
        reader = csv.reader(f, delimiter='\t')
        # skip first one
        next(reader)
        for data in reader:
            d = Document()
            # docid
            d.tags['id'] = int(data[0])
            # doc
            d.text = data[1]
            yield d


def load_pickle(path):
    """Load pickle file.
    ----------
    Arguments:
        path: str file path
    """
    import pickle
    with open(path, 'rb') as f:
        return pickle.load(f)


def evaluate_generator():
    import numpy as np
    test_set = load_pickle('dataset/test_set_50.pickle')
    t = np.array(test_set)
    t = t[:, :2]
    t = t.tolist()

    test = t[:10]

    docid2text = load_pickle('dataset/docid_to_text.pickle')
    qid2text = load_pickle('dataset/qid_to_text.pickle')

    for q_id, matches_doc_id in test:
        query = Document()
        query.tags['id'] = q_id
        query.text = qid2text[q_id]
        groundtruth = Document()
        for match_doc_id in matches_doc_id:
            match = Document()
            match.tags['id'] = match_doc_id
            match.score = NamedScore(value=1.0)
            match.text = docid2text[match_doc_id]
            groundtruth.matches.add(match)

        yield query, groundtruth


def index():
    """
    Index data using Index Flow.
    """
    f = Flow.load_config('flows/index.yml')

    with f:
        f.index(input_fn=index_generator, batch_size=8)


def print_resp(resp, question):
    """
    Print response.
    """
    for d in resp.search.docs:
        print(f"🔮 Ranked list of answers to the question: {question} \n")

        for idx, match in enumerate(d.matches):

            score = match.score.value
            if score < 0.0:
                continue
            answer = match.text.strip()
            print(f'> {idx + 1:>2d}. "{answer}"\n Score: ({score:.2f})')


def print_average_evaluations():
    print(f' Average Evaluation Results')
    print('\n'.join(f'      {name}: {value / num_evaluation_docs}' for name, value in evaluation_value.items()))


def print_evaluation_results(resp):
    global evaluation_value
    global num_evaluation_docs
    for d in resp.search.docs:
        print(f'\n'
              f'Evaluations for QID:{d.tags["id"]} [{d.text}]')
        evaluations = d.evaluations
        for i in range(0, 3):
            evaluation_value[f'Matching-{evaluations[i].op_name}'] += evaluations[i].value
        for i in range(3, 6):
            evaluation_value[f'Ranking-{evaluations[i].op_name}'] += evaluations[i].value

        num_evaluation_docs += 1

        print(f''
              f'    Matching-{evaluations[0].op_name}: {evaluations[0].value} \n'
              f'    Matching-{evaluations[1].op_name}: {evaluations[1].value} \n'
              f'    Matching-{evaluations[2].op_name}: {evaluations[2].value} \n'
              f''
              f'    Ranking-{evaluations[3].op_name}: {evaluations[3].value} \n'
              f'    Ranking-{evaluations[4].op_name}: {evaluations[4].value} \n'
              f'    Ranking-{evaluations[5].op_name}: {evaluations[5].value}')


# for search
def search():
    f = Flow.load_config('flows/query.yml')

    with f:
        while True:
            text = input("Please type a question: ")
            if not text:
                break

            def ppr(x):
                print_resp(x, text)

            f.search_lines(lines=[text, ], output_fn=ppr, top_k=50)


# for evaluate
def evaluate():
    f = Flow.load_config('flows/evaluate.yml')

    with f:
        f.search(input_fn=evaluate_generator, output_fn=print_evaluation_results, top_k=10, batch_size=8)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('choose between "index/search/dryrun" mode')
        exit(1)
    if sys.argv[1] == 'index':
        config()
        index()
    elif sys.argv[1] == 'search':
        config()
        search()
    elif sys.argv[1] == 'evaluate':
        config()
        evaluate()
        print_average_evaluations()
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
