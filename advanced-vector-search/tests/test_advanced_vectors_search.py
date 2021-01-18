import os
import sys

import pytest

sys.path.append('..')
from app import run


@pytest.fixture(scope='session')
def siftsmall_data():
    os.system('./get_siftsmall.sh')
    os.system('./generate_training_data.sh')
    yield


@pytest.fixture(scope='session')
def docker_images():
    if 'GITHUB_WORKFLOW' in os.environ:
        jina_hub_root = os.path.join('/home/runner/work/examples/examples/jinahub')
    else:
        import jina
        jina_root = os.path.dirname(os.path.abspath(jina.__file__))
        jina_hub_root = os.path.join(jina_root, 'hub')

    faiss_indexer_root = os.path.join(jina_hub_root, 'indexers/vector/FaissIndexer')
    os.system(
        f'docker build -f {faiss_indexer_root}/Dockerfile {faiss_indexer_root} -t faiss_indexer_image:test')
    os.environ['JINA_USES_FAISS'] = 'docker://faiss_indexer_image:test'
    annoy_indexer_root = os.path.join(jina_hub_root, 'indexers/vector/AnnoyIndexer')
    os.system(
        f'docker build -f {annoy_indexer_root}/Dockerfile {annoy_indexer_root} -t annoy_indexer_image:test')
    os.environ['JINA_USES_ANNOY'] = 'docker://annoy_indexer_image:test'
    yield
    del os.environ['JINA_USES_FAISS']
    del os.environ['JINA_USES_ANNOY']


@pytest.fixture(scope='session')
def index():
    run(task='index', request_size=50, top_k=100, indexer_query_type='numpy')
    yield


@pytest.mark.parametrize('index_type, expected', [('numpy', 99), ('annoy', 77), ('faiss', 47)])
def test_advanced_search_example(siftsmall_data, docker_images, index, index_type, expected):
    evaluation = run(task='query', request_size=50, top_k=100, indexer_query_type=index_type)
    assert int(evaluation) == expected
