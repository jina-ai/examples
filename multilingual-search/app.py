__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import click
import random
import string
import itertools

from jina.flow import Flow

RANDOM_SEED = 10
random.seed(RANDOM_SEED)

SUPPORTED_LANGUAGES = ['en', 'cs', 'de', 'es', 'fr']
SUPPORTED_YEARS = ['2008', '2009', '2010', '2011', '2012']
INDEX_FLOW_YAML = 'flow-index.yml'
QUERY_FLOW_YAML = 'flow-query.yml'


def get_random_ws(workspace_path, length=8):
    letters = string.ascii_lowercase
    dn = ''.join(random.choice(letters) for i in range(length))
    return os.path.join(workspace_path, dn)


def configure_model(data_dir = '/tmp/jina/multilingual'):
    os.environ['PARALLEL'] = str(2)
    os.environ['SHARDS'] = str(2)
    os.environ['TMP_DATA_DIR'] = data_dir
    os.environ['PATH_TO_BPE_CODES'] = data_dir + '/93langs.fcodes'
    os.environ['PATH_TO_BPE_VOCAB'] = data_dir + '/93langs.fvocab'
    os.environ['PATH_TO_ENCODER'] = data_dir + '/bilstm.93langs.2018-12-26.pt'
    os.environ['WORKDIR'] = get_random_ws(os.environ['TMP_DATA_DIR'])
    

def print_topk(resp, word):
    for doc in resp.search.docs:
        print(f'\n\n\nHere are what we found for: {word}')
        # print(_doc.topk_results)
        for idx, match in enumerate(doc.matches):
            score = match.score.value
            if score < 0.0:
                continue
            text = match.chunks[0].text
            print('> {:>2d}({:.2f}). "{}"'.format(idx, score, text.strip()))


def read_query_data(text):
    yield '{}'.format(text)


def index(documents, size, batch_size=32):
    f = Flow().load_config(INDEX_FLOW_YAML)
    with f:
        f.index_lines(lines=documents,
                      size=size, 
                      batch_size=batch_size)
    print('- Indexing completed!')


def query(top_k):
    f = Flow().load_config(QUERY_FLOW_YAML)
    with f:
        while True:
            text = input('\n\n\n- Please type a sentence to find semantic similarity in multiple languages : ')
            if not text:
                break
            
            ppr = lambda x: print_topk(x, text)
            f.search(read_query_data(text), callback=ppr, top_k=top_k)


@click.command()
@click.option('--task', '-t', help='Allowed values - index, query')
@click.option('--num_docs', '-n', default=None, help='Number of documents to index')
@click.option('--languages', '-l', default='en:fr', help='Allowed values - en, cs, de, es, fr (: delimited)')
@click.option('--years', '-y', default='2011:2012', help='Allowed values - 2008, 2009, 2010, 2011, 2012 (: delimited)')
@click.option('--top_k', '-k', default=5, help='Number of results to rank')
def main(task, num_docs, languages, years, top_k):
    
    languages = languages.split(':')
    [languages.remove(language) for language in languages if language not in SUPPORTED_LANGUAGES]
    print(f'- List of languages to be indexed: {languages}')
    
    years = years.split(':')
    [years.remove(year) for year in years if year not in SUPPORTED_YEARS]
    print(f'- List of years to be indexed: {years}')
    
    filenames = [f'newstest{year}.{language}' for year, language in itertools.product(years, languages)]
    print(f'- Files to be processed: {filenames}')
    
    configure_model()
    
    all_documents = []
    
    for year, language in itertools.product(years, languages):
        with open(f'{os.environ["TMP_DATA_DIR"]}/dev/newstest{year}.{language}') as f:
            all_documents.extend(f.read().splitlines())
    
    if task == 'index':
        workspace = os.environ['WORKDIR']
        if os.path.exists(workspace):
            print(f'\n +---------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                        | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again. | \
                    \n |                                   🤖🤖🤖                                        | \
                    \n +---------------------------------------------------------------------------------+')
        index(documents=all_documents,
              size=num_docs,
              batch_size=16)
        
    elif task == 'query':
        query(top_k=top_k)
    
    else:
        raise NotImplementedError(
            f'Unknown task: {task}. A valid task is either `index` or `query`.')


if __name__ == '__main__':
    main()
