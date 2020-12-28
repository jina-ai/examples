__version__ = '0.0.1'

import os
import sys
from jina.flow import Flow
from jina import Document

num_docs = int(os.environ.get('MAX_DOCS', 10))

def config():
    parallel = 1 if sys.argv[1] == 'index' else 1
    # parallel = 2
    shards = 1

    os.environ['JINA_PARALLEL'] = str(parallel)
    os.environ['JINA_SHARDS'] = str(shards)
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = os.environ.get('JINA_PORT', str(65481))
    os.environ['JINA_DATA_PATH'] = 'dataset/answer_collection.tsv'


def index_generator():
    import csv
    data_path = os.path.join(os.path.dirname(__file__), os.environ['JINA_DATA_PATH'])

    # Get Document and ID
    with open(data_path) as f:
        reader = csv.reader(f, delimiter='\t')
        for i, data in enumerate(reader):
            d = Document()
            d.tags['id'] = int(data[0])
            d.text = data[1]
            d.update_id()
            yield d


def print_resp(resp, question):
    for d in resp.search.docs:
        print(f"Ta-Dah🔮, here are what we found for the question: {question}: \n")

        for idx, match in enumerate(d.matches):

            score = match.score.value
            if score < 0.0:
                continue
            # character = match.meta_info.decode()
            dialog = match.text.strip()
            print(f'> {idx+1:>2d}. "{dialog}"\n Score: ({score:.2f})')


# for index
def index():
    f = Flow.load_config('flows/index.yml')

    with f:
        f.index(input_fn=index_generator, batch_size=16)


# for search
def search():
    f = Flow.load_config('flows/query.yml')

    with f:
        while True:
            text = input("please type a question: ")
            if not text:
                break

            def ppr(x):
                print_resp(x, text)

            f.search_lines(lines=[text, ], output_fn=ppr, top_k=50)


def dryrun():
    f = Flow().load_config("flows/index.yml")
    with f:
        f.dry_run()


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
    elif sys.argv[1] == "dryrun":
        config()
        dryrun()
    else:
        raise NotImplementedError(f'unsupported mode {sys.argv[1]}')
