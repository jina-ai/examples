import subprocess
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


def processes_alive(processes):
    for p in processes:
        if p.poll() is not None:
            return False
    return True


def rolling_update_done(flow_process):
    for l in iter(flow_process.stdout.readline, b''):
        l = l.decode()
        print(l)
        if 'rolling update done.' in l:
            return True
    return False


def test_query_while_indexing():
    try:
        jinad_process = subprocess.Popen('jinad', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        flow_process = subprocess.Popen(
            [sys.executable, '-u', 'app.py', '-t', 'flows'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
        )
        while processes_alive([jinad_process, flow_process]):
            time.sleep(15)
            logger.info('rolling update done in process')
            # add query testing
            query_doc = Document()
            query_doc.text = 'hello world'
            response = _query_docs([query_doc.dict()])
            assert response.json()['search']['docs'][0].get('matches')
            break

        raise RuntimeError(
            f'processes crashed/ended. jinad stderr: {jinad_process.stderr.readlines()}; app.py stderr: {flow_process.stderr.readlines()}'
        )
    except (Exception, KeyboardInterrupt):
        raise
    finally:
        print(jinad_process.stdout.readlines())
        print(flow_process.stdout.readlines())
        jinad_process.kill()
        flow_process.kill()
