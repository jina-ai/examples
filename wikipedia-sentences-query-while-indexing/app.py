__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import time
import traceback
from typing import List, Dict

import click
from daemon.clients import JinaDClient
from jina.logging.logger import JinaLogger
from jina import __default_host__, Document, DocumentArray, Client

os.environ['JINA_LOG_LEVEL'] = 'DEBUG'

HOST = __default_host__  # change this if you are using remote jinad
JINAD_PORT = 8000  # change this if you start jinad on a different port
DUMP_PATH = '/jinad_workspace/dump'  # the path where to dump
SHARDS = 1  # change this if you change pods/query_indexer.yml
DUMP_RELOAD_INTERVAL = 10  # time between dump - rolling update calls
DATA_FILE = 'data/toy.txt'  # change this if you get the full data
DOCS_PER_ROUND = 5  # nr of documents to index in each round
STORAGE_FLOW_YAML_FILE = 'storage.yml'  # indexing Flow yaml name
QUERY_FLOW_YAML_FILE = 'query.yml'  # querying Flow yaml name
STORAGE_REST_PORT = 9000  # REST port of storage Flow, defined in flows/storage.yml
QUERY_REST_PORT = 9001  # REST port of Query Flow, defined in flows/query.yml

logger = JinaLogger('jina')
cur_dir = os.path.dirname(os.path.abspath(__file__))
jinad_client = JinaDClient(host=HOST, port=JINAD_PORT, timeout=10 * 60)


def docarray_from_file(filename):
    docs = []
    with open(filename) as f:
        for line in f:
            docs.append(Document(text=line))
    return DocumentArray(docs)


def query_restful():
    while True:
        text = input('please type a sentence: ')
        if not text:
            break

        query_doc = Document()
        query_doc.text = text
        response = query_docs(query_doc)
        matches = response[0].data.docs[0].matches
        len_matches = len(matches)
        logger.info(f'Ta-Dah🔮, {len_matches} matches we found for: "{text}" :')

        for idx, match in enumerate(matches):
            score = match.scores['euclidean'].value
            if score < 0.0:
                continue
            logger.info(f'> {idx:>2d}({score:.2f}). {match.text}')


def index_docs(docs: List[Dict], round: int):
    docs_to_send = docs[round * DOCS_PER_ROUND : (round + 1) * DOCS_PER_ROUND]
    logger.info(f'Indexing {len(docs_to_send)} document(s)...')
    Client(host=HOST, port=STORAGE_REST_PORT, protocol='http').index(inputs=docs_to_send)


def query_docs(docs: Document):
    logger.info(f'Searching document {docs}...')
    return Client(host=HOST, port=QUERY_REST_PORT, protocol='http').search(inputs=docs, return_results=True)


def create_flows():
    workspace_id = jinad_client.workspaces.create(paths=[os.path.join(cur_dir, 'flows')])
    jinad_workspace = jinad_client.workspaces.get(workspace_id)['metadata']['workdir']

    logger.info('Creating storage Flow...')
    storage_flow_id = jinad_client.flows.create(
        workspace_id=workspace_id, filename=STORAGE_FLOW_YAML_FILE, envs={'JINAD_WORKSPACE': jinad_workspace}
    )
    logger.info(f'Created successfully. Flow ID: {storage_flow_id}')
    logger.info('Creating Query Flow...')
    query_flow_id = jinad_client.flows.create(
        workspace_id=workspace_id, filename=QUERY_FLOW_YAML_FILE, envs={'JINAD_WORKSPACE': jinad_workspace}
    )
    logger.info(f'Created successfully. Flow ID: {query_flow_id}')
    return storage_flow_id, query_flow_id, workspace_id


def dump_and_roll_update(storage_flow_id: str, query_flow_id: str):
    docs = docarray_from_file(DATA_FILE)
    logger.info(f'starting dump and rolling-update process')
    round = 0
    while True:
        logger.info(f'round {round}:')
        index_docs(docs, round)
        current_dump_path = os.path.join(DUMP_PATH, str(round))

        logger.info(f'dumping...')
        Client(host=HOST, port=STORAGE_REST_PORT, protocol='http').post(
            on='/dump',
            parameters={'shards': SHARDS, 'dump_path': current_dump_path},
            target_peapod='storage_indexer',
        )

        # JinaD is used for ctrl requests on Flows
        logger.info(f'performing rolling update across replicas...')
        jinad_client.flows.update(
            id=query_flow_id,
            kind='rolling_update',
            pod_name='query_indexer',
            dump_path=current_dump_path,
        )
        logger.info(f'rolling update done. sleeping for {DUMP_RELOAD_INTERVAL}secs...')
        time.sleep(DUMP_RELOAD_INTERVAL)
        round += 1


def cleanup(storage_flow_id, query_flow_id, workspace_id):
    jinad_client.flows.delete(storage_flow_id)
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
    if task == 'flows':
        # start a Index Flow, dump the data from the Index Flow, and load it into the Query Flow.
        try:
            storage_flow_id, query_flow_id, workspace_id = create_flows()
            # starting a loop that
            # - indexes some data in batches
            # - sends request to storage Flow in JinaD to dump its data to a location
            # - send request to Query Flow in JinaD to perform rolling update across its replicas,
            # which reads the new data in the dump
            dump_and_roll_update(storage_flow_id, query_flow_id)
        except (Exception, KeyboardInterrupt) as e:
            if e:
                logger.warning(f'Caught: {e}. Original stacktrace following:')
                logger.error(traceback.format_exc())
            logger.info('Shutting down and cleaning Flows in JinaD...')
            cleanup(storage_flow_id, query_flow_id, workspace_id)

    elif task == 'client':
        query_restful()


if __name__ == '__main__':
    main()
