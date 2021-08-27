__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import time
import traceback
from pathlib import Path
from typing import List, Dict

import click
from daemon.clients import JinaDClient
from jina.logging.logger import JinaLogger
from jina.types.document.generators import from_files
from jina import __default_host__, Document, DocumentArray, Client


logger = JinaLogger('jina')

cur_dir = os.path.dirname(os.path.abspath(__file__))

HOST = '3.86.211.43'  # change this if you are using remote jinad
JINAD_PORT = '8000'  # change this if you set a different port
jinad_client = JinaDClient(host=HOST, port=JINAD_PORT, timeout=10 * 60)

DUMP_PATH = '/workspace/dump'  # the path where to dump
SHARDS = 3  # change this if you change pods/query_indexer.yml
DUMP_RELOAD_INTERVAL = 60  # time between dump - rolling update calls
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
        response = query_docs(query_doc)
        for doc in response['data']['docs']:
            matches = doc['matches']
            len_matches = len(matches)
            logger.info(f'Ta-Dah🔮, {len_matches} matches we found for: "{text}" :')

            for idx, match in enumerate(matches):
                score = match.scores['distance']
                if score < 0.0:
                    continue
                logger.info(f'> {idx:>2d}({score:.2f}). {match["text"]}')


def index_docs(docs: List[Dict], round: int):
    docs_to_send = docs[round * DOCS_PER_ROUND: (round + 1) * DOCS_PER_ROUND]
    logger.info(f'Indexing {len(docs_to_send)} document(s)...')
    Client(host=HOST, port=DBMS_REST_PORT, protocol='http').post(
        on='index', inputs=docs_to_send
    )


def query_docs(docs: Document):
    logger.info(f'Searching document {docs}...')
    return Client(host=HOST, port=QUERY_REST_PORT, protocol='http').search(
        inputs=docs, return_results=True
    )


def _path_size(dump_path):
    dir_size = (
        sum(f.stat().st_size for f in Path(dump_path).glob('**/*') if f.is_file()) / 1e6
    )
    return dir_size


def create_flows():
    workspace_id = jinad_client.workspaces.create(
        paths=[os.path.join(cur_dir, 'flows')]
    )
    logger.info('Creating DBMS Flow..')
    dbms_flow_id = jinad_client.flows.create(
        workspace_id=workspace_id, filename='dbms.yml'
    )
    logger.info(f'Created successfully. Flow ID: {dbms_flow_id}')
    logger.info('Creating Query Flow:')
    query_flow_id = jinad_client.flows.create(
        workspace_id=workspace_id, filename='query.yml'
    )
    logger.info(f'Created successfully. Flow ID: {query_flow_id}')
    return dbms_flow_id, query_flow_id, workspace_id


def dump_and_roll_update(dbms_flow_id: str, query_flow_id: str):
    docs = DocumentArray(from_files(DATA_FILE))
    logger.info(f'starting dump and rolling-update process')
    round = 0
    while True:
        logger.info(f'round {round}:')
        index_docs(docs, round)
        current_dump_path = os.path.join(DUMP_PATH, str(round))

        logger.info(f'dumping...')
        Client(host=HOST, port_expose=DBMS_REST_PORT, protocol='http').post(
            on='/dump',
            parameters={'shards': SHARDS, 'dump_path': current_dump_path},
            target_peapod='dbms_indexer',
        )

        # JinaD is used for ctrl requests on Flows
        logger.info(f'rolling update across replicas...')
        jinad_client.flows.update(
            id=query_flow_id,
            kind='rolling_update',
            pod_name='query_indexer',
            dump_path=current_dump_path,
        )
        logger.info(f'rolling update done. sleeping...')
        time.sleep(DUMP_RELOAD_INTERVAL)
        round += 1


def cleanup(dbms_flow_id, query_flow_id, workspace_id):
    jinad_client.flows.delete(dbms_flow_id)
    jinad_client.flows.delete(query_flow_id)
    jinad_client.workspaces.delete(workspace_id)


@click.command()
@click.option(
    '--task',
    '-t',
    type=click.Choice(['flows', 'client'], case_sensitive=False),
)
def main(task: str):
    """main entrypoint for this example"""
    # os.environ.setdefault('JINA_WORKSPACE_MOUNT', 'workspace:/workspace/workspace')
    if task == 'flows':
        # start a Index Flow, dump the data from the Index Flow, and load it into the Query Flow.
        try:
            if os.path.exists(DUMP_PATH):
                logger.warning(f'removing {DUMP_PATH}...')
                shutil.rmtree(DUMP_PATH, ignore_errors=False)

            dbms_flow_id, query_flow_id, workspace_id = create_flows()
            # starting a loop that
            # - indexes some data in batches
            # - sends request to DBMS Flow in JinaD to dump its data to a location
            # - send request to Query Flow in JinaD to perform rolling update across its replicas,
            # which reads the new data in the dump
            dump_and_roll_update(dbms_flow_id, query_flow_id)
        except (Exception, KeyboardInterrupt) as e:
            if e:
                logger.warning(f'Caught: {e}. Original stacktrace following:')
                logger.error(traceback.format_exc())
            logger.info('Shutting down and cleaning Flows in JinaD...')
            cleanup(dbms_flow_id, query_flow_id, workspace_id)

    elif task == 'client':
        query_restful()


if __name__ == '__main__':
    main()
