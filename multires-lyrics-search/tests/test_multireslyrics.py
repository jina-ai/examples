__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

__copyright__ = 'Copyright (c) 2020 Jina AI Limited. All rights reserved.'
__license__ = 'Apache-2.0'

import csv
import itertools
import json
import os

import pytest
from jina.flow import Flow
from jina import Document

TOP_K = 3
INDEX_FLOW_FILE_PATH = 'flows/index.yml'
QUERY_FLOW_FILE_PATH = 'flows/query.yml'
PORT = 45678
JINA_SHARDS = 2
JINA_PARALLEL = 1
BATCH_SIZE = 4


# TODO restructure project so we don't duplicate input_fn
def input_fn():
    lyrics_file = os.environ.get('JINA_DATA_FILE')
    with open(lyrics_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in itertools.islice(reader, int(os.environ.get('JINA_MAX_DOCS'))):
            if row[-1] == 'ENGLISH':
                with Document() as d:
                    d.tags['ALink'] = row[0]
                    d.tags['SName'] = row[1]
                    d.tags['SLink'] = row[2]
                    d.text = row[3]
                yield d


def config(tmpdir):
    os.environ.setdefault('JINA_MAX_DOCS', '100')
    os.environ.setdefault('JINA_PARALLEL', str(JINA_PARALLEL))
    os.environ.setdefault('JINA_SHARDS', str(JINA_SHARDS))
    os.environ.setdefault('JINA_WORKSPACE', str(tmpdir))
    os.environ.setdefault('JINA_DATA_FILE', 'tests/data-index.csv')
    os.environ.setdefault('JINA_PORT', str(PORT))

    os.makedirs(os.environ['JINA_WORKSPACE'], exist_ok=True)
    return


def index_documents():
    f = Flow().load_config(INDEX_FLOW_FILE_PATH)

    with f:
        f.index(input_fn, batch_size=BATCH_SIZE)


def call_api(url, payload=None, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json; charset=utf-8'}
    import requests

    return requests.post(url, data=json.dumps(payload), headers=headers).json()


def get_results(query, top_k=TOP_K):
    return call_api(
        f'http://0.0.0.0:{PORT}/api/search', payload={'top_k': top_k, 'data': [query]}
    )


def get_flow():
    f = Flow().load_config(QUERY_FLOW_FILE_PATH)
    f.use_rest_gateway()
    return f


@pytest.fixture
def queries_and_expected_replies():
    return json.load(open('tests/query_results.json', 'r'))


def test_query(tmpdir, queries_and_expected_replies):
    def extract_score_value(x):
        return x['value'] if 'value' in x else 0.0

    config(tmpdir)
    index_documents()
    f = get_flow()
    with f:
        for query, exp_result in queries_and_expected_replies:
            output = get_results(query)

            # chunk-level comparison
            chunks = output['search']['docs'][0]['chunks']
            query_chunk_results = []
            for chunk in chunks:
                chunk_result = {'chunk': chunk['text'], 'chunk_matches': []}
                chunk_matches = chunk['matches']
                # make sure to sort in asc. order, by score
                chunk_matches = sorted(chunk_matches, key=lambda x: extract_score_value(x['score']), reverse=False)
                for match in chunk_matches:
                    chunk_result['chunk_matches'].append(match['text'])
                query_chunk_results.append(chunk_result)
            assert query_chunk_results == exp_result["chunk-level"]

            # match-level comparison
            matches = output['search']['docs'][0]['matches']
            # make sure to sort in asc. order, by score
            matches = sorted(matches, key=lambda x: extract_score_value(x['score']), reverse=False)
            match_result = []
            for match in matches:
                match_text = match['text']
                match_result.append(match_text)
            assert match_result == exp_result["match-level"]

            # check the number of docs returned
            # note. the TOP K reflects nr of matches per chunk
            assert len(matches) <= TOP_K * JINA_SHARDS
