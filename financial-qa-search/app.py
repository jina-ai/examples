__version__ = '0.0.1'

import os
import sys
from collections import defaultdict

from jina.flow import Flow
from jina import Document

evaluation_value = defaultdict(float)
num_evaluation_docs = 0


def config():
    """
    Configure environment variables.
    """
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


def search():
    """
    Search results using Query Flow.
    """
    f = Flow.load_config('flows/query.yml')

    with f:
        while True:
            text = input("Please type a question: ")
            if not text:
                break

            def ppr(x):
                print_resp(x, text)

            f.search_lines(lines=[text, ], output_fn=ppr, top_k=50)


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
    """
    Create two Documents - query and groundtruth to store question id and text and groundtruth answer id and text.
    """
    test_set = load_pickle('dataset/sample_test_set.pickle')
    # Convert docid to answer text
    docid2text = load_pickle('dataset/docid_to_text.pickle')
    # Convert qid to question text
    qid2text = load_pickle('dataset/qid_to_text.pickle')

    for q_id, matches_doc_id in test_set:
        # Create query Document
        query = Document()
        # Store question id and text in Document
        query.tags['id'] = q_id
        query.text = qid2text[q_id]

        # Create groundtruth Document
        groundtruth = Document()
        for match_doc_id in matches_doc_id:
            match = Document()
            # Store groundtruth answer id and text in Document
            match.tags['id'] = match_doc_id
            match.text = docid2text[match_doc_id]
            groundtruth.matches.add(match)

        yield query, groundtruth


def print_average_evaluations():
    """
    Compute average precision and reciprocal rank.
    """
    print(f' Average Evaluation Results')
    print('\n'.join(f'      {name}: {value / num_evaluation_docs}' for name, value in evaluation_value.items()))


def print_evaluation_results(resp):
    """
    Print evaluation results before and after reranking.
    """
    global evaluation_value
    global num_evaluation_docs
    for d in resp.search.docs:
        print(f'\n'
              f'Evaluations for QID:{d.tags["id"]} [{d.text}]')
        evaluations = d.evaluations

        evaluation_value[f'Matching-Precision@10'] += evaluations[0].value
        evaluation_value[f'Matching-ReciprocalRank@10'] += evaluations[1].value
        evaluation_value[f'Ranking-Precision@10'] += evaluations[2].value
        evaluation_value[f'Ranking-ReciprocalRank@10'] += evaluations[3].value

        num_evaluation_docs += 1

        print(f''
              f'    Matching-Precision@10: {evaluations[0].value} \n'
              f'    Matching-ReciprocalRank@10: {evaluations[1].value} \n'
              f''
              f'    Ranking-Precision@10: {evaluations[2].value} \n'
              f'    Ranking-ReciprocalRank@10: {evaluations[3].value} \n')


def evaluate():
    """
    Evaluate results using Evaluate Flow.
    """
    f = Flow.load_config('flows/evaluate.yml')

    with f:
        f.search(input_fn=evaluate_generator, output_fn=print_evaluation_results, top_k=10, batch_size=1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('choose between "index/search/evaluate" mode')
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
