__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import time
import traceback
from contextlib import ExitStack
from pathlib import Path
from typing import List, Dict, Optional

import click
import requests
from daemon.models import DaemonID
from jina import __default_host__, Document, DocumentArray, Flow
from jina.enums import RemoteWorkspaceState
from jina.logging.logger import JinaLogger
from jina.types.document.generators import from_files


logger = JinaLogger('jina')

cur_dir = os.getcwd()

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
        for doc in response['data']['docs']:
            matches = doc['matches']
            len_matches = len(matches)
            logger.info(f'Ta-Dah🔮, {len_matches} matches we found for: "{text}" :')

            for idx, match in enumerate(matches):
                score = match.scores['distance']
                if score < 0.0:
                    continue
                logger.info(f'> {idx:>2d}({score:.2f}). {match["text"]}')


def _jinad_url(host: str, port: int, kind: str):
    return f'http://{host}:{port}/{kind}'


def wait_for_workspace(
    workspace_id: DaemonID,
    host: str = __default_host__,
    port: int = 8000,
) -> bool:
    url = _jinad_url(host, port, 'workspaces')
    while True:
        r = requests.get(f'{url}/{workspace_id}')
        try:
            state = r.json()['state']
        except KeyError as e:
            print(f'KeyError: {e!r}')
            return False
        if state in [
            RemoteWorkspaceState.PENDING,
            RemoteWorkspaceState.CREATING,
            RemoteWorkspaceState.UPDATING,
        ]:
            print(f'workspace still {state}, sleeping for 2 secs')
            time.sleep(2)
            continue
        elif state == RemoteWorkspaceState.ACTIVE:
            print(f'workspace got created successfully')
            return True
        elif state == RemoteWorkspaceState.FAILED:
            print(f'workspace creation failed. please check logs')
            return False


def _create_workspace(
    filepaths: Optional[List[str]] = None,
    dirpath: Optional[str] = None,
    workspace_id: Optional[DaemonID] = None,
    url: Optional[str] = None
) -> Optional[str]:
    with ExitStack() as file_stack:

        def _to_file_tuple(path):
            return 'files', file_stack.enter_context(open(path, 'rb'))

        files_to_upload = set()
        if filepaths:
            files_to_upload.update([_to_file_tuple(filepath) for filepath in filepaths])
        if dirpath:
            for ext in ['*yml', '*yaml', '*py', '*.jinad', 'requirements.txt']:
                files_to_upload.update(
                    [_to_file_tuple(filepath) for filepath in Path(dirpath).rglob(ext)]
                )

        if not files_to_upload:
            print('nothing to upload')
            return

        print(f'will upload files: {files_to_upload}')
        r = requests.post(url, files=list(files_to_upload))
        print(f'Checking if the upload is succeeded: {r.json()}')
        assert r.status_code == 201
        json_response = r.json()
        workspace_id = next(iter(json_response))
        return workspace_id


def create_flow(
    workspace_id: DaemonID,
    filename: str,
    host: str = __default_host__,
    port: int = 8000,
) -> str:
    url = _jinad_url(host, port, 'flows')
    r = requests.post(url, params={'workspace_id': workspace_id, 'filename': filename})

    assert r.status_code == 201
    return r.json()

def _serve_flow_with_workspace(
    flow_yaml: str,
    deps: List[str] = []
) -> str:
    flow_url = _jinad_url(JINAD_HOST, JINAD_PORT, 'flows')
    ws_url = _jinad_url(JINAD_HOST, JINAD_PORT, 'workspaces')
    deps.append(flow_yaml)
    deps.append('requirements.txt')
    workspace_id = _create_workspace(filepaths=[os.path.join(cur_dir, file) for file in deps], url=ws_url)
    # with open(flow_yaml, 'rb') as f:
    #     print(f'filename {f}')
    assert(wait_for_workspace(workspace_id=workspace_id, host=JINAD_HOST))
    #with open(flow_yaml, 'rb') as f:
    r = requests.post(flow_url, params={'workspace_id': workspace_id, 'filename': flow_yaml.split('/')[-1]})
    #r = requests.post(flow_url, data={'workspace_id': workspace_id}, files={'flow': f})
    print(f'Checking if the flow creation is succeeded: {r.json()}')
    assert r.status_code == 201
    return r.json(), workspace_id


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


def _send_rest_request(port_expose: str, endpoint: str, method: str, data: List[dict], timeout: int = 13000000):
    json = {'data': ['test data']}
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
    return DocumentArray(from_files(file))



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
#     workspace_ids,
#     host: str = __default_host__,
#     port: int = 8000,
# ) -> bool:
#     for workspace_id in workspace_ids:
#         print(f'will delete workspace {workspace_id}')
#         url = _jinad_url(host, port, f'workspaces/{workspace_id}')
#         r = requests.delete(url, params={'everything': True})
#         assert(r.status_code == 200)
    url = f'http://{JINAD_HOST}:{JINAD_PORT}/workspaces/'
    r = requests.delete(url, params={'everything': True})



@click.command()
@click.option(
    '--task',
    '-t',
    type=click.Choice(['flows', 'client'], case_sensitive=False),
)
def main(task: str):
    """main entrypoint for this example"""
    os.environ.setdefault('JINA_WORKSPACE_MOUNT', 'workspace:/workspace/workspace')
    if task == 'flows':
        # start a Index Flow, dump the data from the Index Flow, and load it into the Query Flow.
        try:
            if os.path.exists(DUMP_PATH):
                logger.warning(f'removing {DUMP_PATH}...')
                shutil.rmtree(DUMP_PATH, ignore_errors=False)

            # we need to keep track of the Flow id
            dbms_flow_id, dbms_ws = _serve_flow_with_workspace('flows/dbms.yml')
            logger.info(f'created DBMS Flow with id {dbms_flow_id}')

            # we need to keep track of the Flow id
            query_flow_id, query_ws = _serve_flow_with_workspace('flows/query.yml')
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
