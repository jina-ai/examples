__copyright__ = 'Copyright (c) 2020 Jina AI Limited. All rights reserved.'
__license__ = 'Apache-2.0'

import csv
import itertools
import json
import os
import sys
import subprocess

from jina.flow import Flow
import pytest
from jina.proto import jina_pb2

TOP_K = 3
INDEX_FLOW_FILE_PATH = 'flows/index.yml'
QUERY_FLOW_FILE_PATH = 'flows/query.yml'
PORT = 45678


# TODO restructure project so we don't duplicate input_fn
def input_fn():
    lyrics_file = os.environ.get('JINA_DATA_FILE')
    with open(lyrics_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in itertools.islice(reader, int(os.environ.get('JINA_MAX_DOCS'))):
            if row[-1] == 'ENGLISH':
                d = jina_pb2.Document()
                d.tags['ALink'] = row[0]
                d.tags['SName'] = row[1]
                d.tags['SLink'] = row[2]
                d.text = row[3]
                yield d


def config(tmpdir):
    parallel = 2 if sys.argv[1] == 'index' else 1

    os.environ.setdefault('JINA_MAX_DOCS', '100')
    os.environ.setdefault('JINA_PARALLEL', str(parallel))
    os.environ.setdefault('JINA_SHARDS', str(1))
    os.environ.setdefault('JINA_WORKSPACE', str(tmpdir))
    os.environ.setdefault('JINA_DATA_FILE', 'tests/data-index.csv')
    os.environ.setdefault('JINA_PORT', str(PORT))

    os.makedirs(os.environ['JINA_WORKSPACE'], exist_ok=True)
    return


def index_documents():
    f = Flow().load_config(INDEX_FLOW_FILE_PATH)

    with f:
        f.index(input_fn)


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
    return [
        (
            'Take me now, baby, here as I am. Hold me close, and try and understand. Desire is hunger is',
            [
                {
                    'chunk': 'Take me now, baby, here as I am.',
                    'chunk_matches': [
                        'Take me now, baby, here as I am.',
                        'so take me now, take me now, take me now.',
                        'Let me be let me close my eyes.',
                    ],
                },
                {
                    'chunk': 'Hold me close, and try and understand.',
                    'chunk_matches': [
                        'Hold me close, and try and understand.',
                        'Take me along to the places.',
                        'See the signs and know their meaning.',
                    ],
                },
                {
                    'chunk': 'Desire is hunger is',
                    'chunk_matches': [
                        'Desire is hunger is the fire I breathe.',
                        'and fear in life.',
                        'and fear in life.',
                    ],
                },
            ],
        ),
        (
            'I could feel at the time',
            [
                {
                    'chunk': 'I could feel at the time',
                    'chunk_matches': [
                        'I could feel at the time.',
                        'A lie to.',
                        'O, never mind it.',
                    ],
                }
            ],
        ),
        (
            'I promise.',
            [
                {
                    'chunk': 'I promise.',
                    'chunk_matches': [
                        'Never before and never since, I promise.',
                        'truth for life.',
                        "I'll discuss this in the morning,.",
                    ],
                }
            ],
        ),
        (
            'Trudging slowly',
            [
                {
                    'chunk': 'Trudging slowly',
                    'chunk_matches': [
                        'Trudging back over pebbles and sand.',
                        'Trudging slowly over wet sand.',
                        'With desire to be part of the miracles.',
                    ],
                }
            ],
        ),
    ]


def test_query(tmpdir, queries_and_expected_replies):
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
                for match in chunk['matches']:
                    chunk_result['chunk_matches'].append(match['text'])
                query_chunk_results.append(chunk_result)
            assert exp_result == query_chunk_results

            # check the number of docs returned
            matches = output['search']['docs'][0]['matches']
            # note. the TOP K reflects nr of matches per chunk
            assert len(matches) <= TOP_K * len(chunks)
