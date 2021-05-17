import os
import sys
import time
from typing import List, Dict

import requests
from jina import Document
from jina.logging import JinaLogger

logger = JinaLogger('test')


def _query_docs(docs: List[Dict]):
    logger.info(f'Searching with {len(docs)} documents...')
    return _send_rest_request('9001', 'search', 'post', docs)


def _send_rest_request(port_expose: str, endpoint: str, method: str, data: List[dict], timeout: int = 13):
    json = {'data': data}
    url = f'http://localhost:{port_expose}/{endpoint}'
    r = getattr(requests, method)(url, json=json, timeout=timeout)

    if r.status_code != 200:
        raise Exception(f'api request failed, url: {url}, status: {r.status_code}, content: {r.content} data: {data}')
    return r.json()


def test_query_while_indexing():
    try:
        logger.info('starting jinad...')
        os.system('nohup jinad > jinad.log 2> jinaderr.log &')
        time.sleep(5)
        logger.info('starting app.py...')
        os.system(f'nohup {sys.executable} -u app.py -t flows > flow.log 2> flowerr.log &')
        time.sleep(20)
        logger.info('rolling update done in process')
        # add query testing
        query_doc = Document()
        query_doc.text = 'hello world'
        response = _query_docs([query_doc.dict()])
        matches = response['search']['docs'][0].get('matches')
        logger.info(f'got {len(matches)} matches')
        assert matches

    except (Exception, KeyboardInterrupt):
        raise
    finally:
        logger.warning('entering finally...')
        os.system('pkill jinad')
        os.system(f'pkill {sys.executable}')
        logger.warning('following is output from .log files:')
        os.system(f'cat *.log')
