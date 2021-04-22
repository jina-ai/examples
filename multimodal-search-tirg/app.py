__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import sys

import click
import requests
import matplotlib.pyplot as plt

from jina.flow import Flow
from jina import Document
from jina.clients.sugary_io import _input_files
from jina.clients.sugary_io import _input_lines
from jina.logging import default_logger as logger
from jina.types.document.multimodal import MultimodalDocument

num_docs = 100
data_path = 'data/**/*.jpeg'
batch_size = 8
TOP_K = 5


def clean_workdir():
    if os.path.exists(os.environ['JINA_WORKSPACE']):
        shutil.rmtree(os.environ['JINA_WORKSPACE'])
        logger.warning('Workspace deleted')


def config():
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '1')
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_PARALLEL', '2')
    os.environ['JINA_WORKSPACE'] = './workspace'
    os.makedirs(os.environ['JINA_WORKSPACE'], exist_ok=True)
    os.environ['JINA_PORT'] = '45678'


def index_restful(num_docs):
    f = Flow().load_config('flows/index.yml')

    with f:
        data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None))
        print(f'Indexing {data_path}')
        url = f'http://0.0.0.0:{f.port_expose}/index'

        input_docs = _input_lines(
            filepath=data_path,
            size=num_docs,
            read_mode='r',
        )
        data_json = {'data': [Document(text=text).dict() for text in input_docs]}
        print(f'#### {len(data_json["data"])}')
        r = requests.post(url, json=data_json)
        if r.status_code != 200:
            raise Exception(f'api request failed, url: {url}, status: {r.status_code}, content: {r.content}')


def query_restful():
    f = Flow().load_config("flows/query.yml")
    f.use_rest_gateway()
    with f:
        f.block()

def dryrun():
    f = Flow().load_config("flows/index.yml")
    with f:
        pass

def plot_topk_images(images):
    n_row = 1
    n_col = len(images)
    _, axs = plt.subplots(n_row, n_col, figsize=(10, 10))
    axs = axs.flatten()
    for img, ax in zip(images, axs):
        ax.axis('off')
        ax.imshow(img)
    plt.show()


def index_generator(data_path, num_docs):
    for buffer in _input_files(data_path, True, num_docs, None, 'rb'):
        with Document() as doc:
            doc.buffer = buffer
            doc.mime_type = 'image/jpeg'
        yield doc


def uri2image(uri):
    import io
    from base64 import b64decode
    from PIL import Image
    header, encoded = uri.split(",", 1)
    image_data = b64decode(encoded)
    return Image.open(io.BytesIO(image_data))


def print_result(resp):
    images = []
    for i in range(TOP_K):
        image_data_uri = resp.search.docs[0].matches[i].uri
        image = uri2image(image_data_uri)
        images.append(image)
    plot_topk_images(images)


def query_generator(image_paths, text_queries):
    for image_path, text in zip(image_paths, text_queries):
        with open(image_path, 'rb') as fp:
            buffer = fp.read()
        yield MultimodalDocument(modality_content_map={'image': buffer, 'text': text})


@click.command()
@click.option('--task', '-t', type=click.Choice(['index', 'query', 'index_restful', 'query_restful', 'dryrun'], case_sensitive=False))
@click.option('--data_path', '-p', default=data_path)
@click.option('--num_docs', '-n', default=num_docs)
@click.option('--batch_size', '-b', default=batch_size)
@click.option('--image_path', '-ip', default='data/images/dresses/casual_and_day_dresses/58648388/58648388_2.jpeg')
@click.option('--text_query', '-tq', default='change color to black')
@click.option('--overwrite_workspace', '-overwrite', default=True)
def main(task, data_path, num_docs, batch_size, image_path, text_query, overwrite_workspace):
    config()
    image_paths = [image_path]
    text_queries = [text_query]
    workspace = os.environ["JINA_WORKSPACE"]
    if 'index' in task:
        if os.path.exists(workspace):
            print(
                f'\n +------------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                           | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                           | \
                    \n +------------------------------------------------------------------------------------+'
            )
            sys.exit(1)

    print(f'### task = {task}')
    if task == 'index':
        if overwrite_workspace:
            clean_workdir()
        f = Flow.load_config('flow-index.yml')
        with f:
            f.index(index_generator(data_path, num_docs), batch_size=batch_size)
    elif task == 'index_restful':
        index_restful(num_docs)
    elif task == 'query':
        f = Flow.load_config('flow-query.yml')
        with f:
            f.search(input_fn=query_generator(image_paths, text_queries), on_done=print_result)
    elif task == 'query_restful':
        if not os.path.exists(workspace):
            print(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
        query_restful()
    elif task == 'dryrun':
        dryrun()


if __name__ == '__main__':
    main()
