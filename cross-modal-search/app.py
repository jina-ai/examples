__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys

import click
from jina import Flow, Document, DocumentArray
import logging
import matplotlib.pyplot as plt

from dataset import input_index_data

MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 10000))
cur_dir = os.path.dirname(os.path.abspath(__file__))


def config():
    os.environ.setdefault('JINA_WORKSPACE', os.path.join(cur_dir, 'workspace'))
    os.environ.setdefault(
        'JINA_WORKSPACE_MOUNT',
        f'{os.environ.get("JINA_WORKSPACE")}:/workspace/workspace')
    os.environ.setdefault('JINA_LOG_LEVEL', 'INFO')
    os.environ.setdefault('JINA_PORT', str(45678))


def index_restful():
    flow = Flow().load_config('flows/flow-index.yml', override_with={'protocol': 'http'})
    with flow:
        flow.block()


def check_query_result(results, img_uri):
    text_doc = Document(results[0])
    image_doc = Document(results[1])
    # Image doc matches are text:
    print(f'Searching with image {img_uri}. Matches:')
    if image_doc.matches:
        for m in image_doc.matches:
            print(
                f'\t+- {m.id[:10]},\
                score: {m.scores["cosine"].value},\
                text: {m.text}, modality: {m.modality},\
                uri: {m.uri[:20]}'
             )
    
    # Text doc matches are images
    print(f'Searching with text "{text_doc.text}". Matches:')
    if text_doc.matches:
        f, axarr = plt.subplots(1, len(text_doc.matches))

        for i, m in enumerate(text_doc.matches):
            print(f'\t- score: {m.scores["cosine"].value}, modality: {m.modality}, '
                  f'blob: {len(m.blob)}')
            axarr[i].title.set_text(f'score={m.scores["cosine"].value:.3f}')
            axarr[i].imshow(m.blob)
            axarr[i].axes.xaxis.set_visible(False)
            axarr[i].axes.yaxis.set_visible(False)
        plt.suptitle(f"Best matches for '{text_doc.text}'")
        plt.show()


def index(data_set, num_docs, request_size):
    flow = Flow().load_config('flows/flow-index.yml')
    with flow:
        flow.post(on='/index',
                  inputs=input_index_data(num_docs, request_size, data_set),
                  request_size=request_size,
                  show_progress=True)


def query():
    flow = Flow().load_config('flows/flow-query.yml')
    with flow:
        img_uri = 'toy-data/images/1000268201_693b08cb0e.jpg'
        text_doc = Document(text='a black dog and a spotted dog are fighting',
                            modality='text')
        image_doc = Document(uri=img_uri,
                             modality='image')
        import time
        start = time.time()
        result_text = flow.post(on='/search', inputs=text_doc,
                                return_results=True)
        result_image = flow.post(on='/search', inputs=image_doc,
                                 return_results=True)
        print(f'Request duration: {time.time() - start}')
        check_query_result([result_text[0].data.docs[0], result_image[0].data.docs[
            0]], img_uri)



def query_restful():
    flow = Flow(cors=True).load_config('flows/flow-query.yml')
    flow.rest_api = True
    flow.protocol = 'http'
    with flow:
        flow.block()


@click.command()
@click.option('--task', '-t', type=click.Choice(['index', 'index_restful', 'query_restful', 'query']), default='index')
@click.option("--num_docs", "-n", default=MAX_DOCS)
@click.option('--request_size', '-s', default=16)
@click.option('--data_set', '-d', type=click.Choice(['f30k', 'f8k', 'toy-data'], case_sensitive=False), default='toy-data')
def main(task, num_docs, request_size, data_set):
    config()
    workspace = os.environ['JINA_WORKSPACE']
    logger = logging.getLogger('cross-modal-search')
    if 'index' in task:
        if os.path.exists(workspace):
            logger.error(
                f'\n +------------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                           | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                           | \
                    \n +------------------------------------------------------------------------------------+'
            )
            sys.exit(1)
    if 'query' in task:
        if not os.path.exists(workspace):
            logger.error(f'The directory {workspace} does not exist. Please index first via `python app.py -t index`')
            sys.exit(1)

    if task == 'index':
        index(data_set, num_docs, request_size)
    elif task == 'index_restful':
        index_restful()
    elif task == 'query':
        query()
    elif task == 'query_restful':
        query_restful()


if __name__ == '__main__':
    main()
