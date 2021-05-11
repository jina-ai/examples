import os
import sys

import pytest

sys.path.append('..')
from app import run, general_config

DATASET_NAME = 'siftsmall'

@pytest.fixture(scope='session')
def sift_data():
    os.system(f'./get_data.sh {DATASET_NAME}')
    os.system('./generate_training_data.sh')
    yield


@pytest.fixture(scope='session')
def index():
    run(task='index', top_k=100, indexer_query_type='numpy')
    yield


@pytest.mark.parametrize('index_type, expected', [('numpy', 90), ('annoy', 43), ('faiss', 30)])
def test_advanced_search_example(sift_data, index, index_type, expected):
    evaluation = run(task='query', top_k=100, indexer_query_type=index_type)
    assert int(evaluation) >= expected
