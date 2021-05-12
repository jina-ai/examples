__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import time
import traceback
from contextlib import ExitStack
from pathlib import Path
from typing import List, Dict

import click
import requests
from jina import Document
from jina.clients.sugary_io import _input_lines
from jina.logging import JinaLogger

logger = JinaLogger('jina')

curdir = os.getcwd()

JINAD_HOST = 'localhost'  # change this if you are using remote jinad
JINAD_PORT = '8000'  # change this if you set a different port
DUMP_PATH = '/tmp/jina_dump'  # the path where to dump
SHARDS = 3  # change this if you change pods/query_indexer.yml
DUMP_RELOAD_INTERVAL = 20  # time between dump - rolling update calls
DATA_FILE = 'data/toy.txt'  # change this if you get the full data
DOCS_PER_ROUND = 5  # nr of documents to index in each round
DBMS_REST_PORT = '9000'  # REST port of DBMS Flow, defined in flows/dbms.yml
QUERY_REST_PORT = '9001'  # REST port of Query Flow, defined in flows/query.yml


def query_restful():
    while True:
        text = input('please type a sentence: ')
        if not text:
            break

        query_doc = Document()
        query_doc.text = text
        response = _query_docs([query_doc.dict()])

        for doc in response['search']['docs']:
            matches = doc.get('matches')
            len_matches = len(matches)
            logger.info(f'Ta-Dah🔮, {len_matches} matches we found for: "{text}" :')

            for idx, match in enumerate(matches):
                score = match['score']['value']
                if score < 0.0:
                    continue
                logger.info(f'> {idx:>2d}({score:.2f}). {match["text"]}')


def _create_workspace(filepaths: List[str], url: str) -> str:
    with ExitStack() as file_stack:
        files = [('files', file_stack.enter_context(open(filepath, 'rb'))) for filepath in filepaths]
        r = requests.post(url, files=files)
        assert r.status_code == 201
        workspace_id = r.json()
        return workspace_id


def _serve_flow(
    flow_yaml: str,
    deps: List[str],
    flow_url: str = f'http://{JINAD_HOST}:{JINAD_PORT}/flows',
    ws_url: str = f'http://{JINAD_HOST}:{JINAD_PORT}/workspaces',
) -> str:
    workspace_id = _create_workspace(deps, url=ws_url)
    with open(flow_yaml, 'rb') as f:
        r = requests.post(flow_url, data={'workspace_id': workspace_id}, files={'flow': f})
        assert r.status_code == 201
        return r.json()


def _jinad_dump(pod_name: str, dump_path: str, shards: int, url: str):
    params = {
        'kind': 'dump',
        'pod_name': pod_name,
        'dump_path': dump_path,
        'shards': shards,
    }
    # url params
    r = requests.put(url, params=params)
    assert r.status_code == 200


def _send_rest_request(port_expose: str, endpoint: str, method: str, data: List[dict], timeout: int = 13):
    json = {'data': data}
    url = f'http://{JINAD_HOST}:{port_expose}/{endpoint}'
    r = getattr(requests, method)(url, json=json, timeout=timeout)

    if r.status_code != 200:
        raise Exception(f'api request failed, url: {url}, status: {r.status_code}, content: {r.content} data: {data}')
    return r.json()


def _jinad_rolling_update(pod_name: str, dump_path: str, url: str):
    params = {
        'kind': 'rolling_update',
        'pod_name': pod_name,
        'dump_path': dump_path,
    }
    # url params
    r = requests.put(url, params=params)
    assert r.status_code == 200


def _index_docs(docs: List[Dict], round: int):
    docs_to_send = docs[round * DOCS_PER_ROUND : (round + 1) * DOCS_PER_ROUND]
    logger.info(f'Indexing {len(docs_to_send)} documents...')
    _send_rest_request(DBMS_REST_PORT, 'index', 'post', docs_to_send)


def _query_docs(docs: List[Dict]):
    logger.info(f'Searching with {len(docs)} documents...')
    return _send_rest_request(QUERY_REST_PORT, 'search', 'post', docs)


def _docs_from_file(file: str):
    docs = []
    for text in list(_input_lines(filepath=file)):
        d = Document()
        d.text = text
        docs.append(d.dict())
    return docs


def _path_size(dump_path):
    dir_size = sum(f.stat().st_size for f in Path(dump_path).glob('**/*') if f.is_file()) / 1e6
    return dir_size


def _dump_roll_update(dbms_flow_id: str, query_flow_id: str):
    docs = _docs_from_file(DATA_FILE)
    logger.info(f'starting _dump_roll_update process')
    round = 0
    while True:
        logger.info(f'round {round}:')
        _index_docs(docs, round)
        this_dump_path = os.path.join(DUMP_PATH, str(round))

        # JinaD is used for ctrl requests on Flows
        logger.info(f'dumping...')
        _jinad_dump(
            'dbms_indexer',
            this_dump_path,
            SHARDS,
            f'http://{JINAD_HOST}:{JINAD_PORT}/flows/{dbms_flow_id}',
        )

        dir_size = _path_size(this_dump_path)
        assert dir_size > 0
        logger.info(f'dump path size: {dir_size}')

        # JinaD is used for ctrl requests on Flows
        logger.info(f'rolling update across replicas...')
        _jinad_rolling_update(
            'query_indexer',
            this_dump_path,
            f'http://{JINAD_HOST}:{JINAD_PORT}/flows/{query_flow_id}',
        )
        logger.info(f'rolling update done. sleeping...')
        time.sleep(DUMP_RELOAD_INTERVAL)
        round += 1


def _cleanup():
    r = requests.delete(f'http://{JINAD_HOST}:{JINAD_PORT}/workspaces/')
    assert r.status_code == 200
    requests.delete(f'http://{JINAD_HOST}:{JINAD_PORT}/flows/')
    assert r.status_code == 200


@click.command()
@click.option(
    '--task',
    '-t',
    type=click.Choice(['flows', 'client'], case_sensitive=False),
)
def main(task: str):
    """main entrypoint for this example"""
    if task == 'flows':
        try:
            if os.path.exists(DUMP_PATH):
                logger.warning(f'removing {DUMP_PATH}...')
                shutil.rmtree(DUMP_PATH, ignore_errors=False)

            # dependencies required by JinaD in order to start DBMS (Index) Flow
            dbms_deps = ['pods/encoder.yml', 'pods/dbms_indexer.yml']
            # we need to keep track of the Flow id
            dbms_flow_id = _serve_flow('flows/dbms.yml', dbms_deps)
            logger.info(f'created DBMS Flow with id {dbms_flow_id}')

            # dependencies required by JinaD in order to start Query Flow
            query_deps = ['pods/encoder.yml', 'pods/query_indexer.yml']
            # we need to keep track of the Flow id
            query_flow_id = _serve_flow('flows/query.yml', query_deps)
            logger.info(f'created Query Flow with id {query_flow_id}')

            # starting a loop that
            # - indexes some data in batches
            # - sends request to DBMS Flow in JinaD to dump its data to a location
            # - send request to Query Flow in JinaD to perform rolling update across its replicas,
            # which reads the new data in the dump
            _dump_roll_update(dbms_flow_id, query_flow_id)
        except (Exception, KeyboardInterrupt) as e:
            if e:
                logger.warning(f'Caught: {e}. Original stacktrace following:')
                logger.error(traceback.format_exc())
            logger.info('Shutting down and cleaning Flows in JinaD...')
            _cleanup()

    elif task == 'client':
        query_restful()


if __name__ == '__main__':
    main()
