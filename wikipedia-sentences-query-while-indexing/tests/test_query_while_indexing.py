import time
from threading import Thread

from jina import Document, __default_host__, Client
from daemon.clients import JinaDClient
from jina.logging.logger import JinaLogger

HOST = __default_host__
JINAD_PORT = 8000
QUERY_REST_PORT = 9001
logger = JinaLogger('test')


def query_docs(docs: Document):
    logger.info(f'Searching document {docs}...')
    return Client(host=HOST, port=QUERY_REST_PORT, protocol='http').search(inputs=docs, return_results=True)


def test_query_while_indexing():
    try:
        from app import create_flows, dump_and_roll_update

        jinad_client = JinaDClient(host=HOST, port=JINAD_PORT)
        assert jinad_client.alive, 'cannot reach jinad'

        storage_flow_id, query_flow_id, workspace_id = create_flows()
        # start rolling update in the background
        Thread(target=dump_and_roll_update, args=(storage_flow_id, query_flow_id), daemon=True).start()

        logger.info('sleeping for 30 secs to allow 1 round of index, dump & rolling update')
        time.sleep(30)
        query_doc = Document(text='hello world')
        response = query_docs(query_doc)
        matches = response[0].data.docs[0].matches
        logger.info(f'got {len(matches)} matches')
        assert matches

    except (Exception, KeyboardInterrupt):
        raise

    finally:
        from app import cleanup

        cleanup(storage_flow_id, query_flow_id, workspace_id)
