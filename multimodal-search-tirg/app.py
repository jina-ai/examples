__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import shutil
import sys

import click

from jina.flow import Flow
from jina.logging import default_logger as logger
from jina.proto import jina_pb2
from jina.proto import uid


num_docs = 8
data_path = 'data/*/*.jpeg'
batch_size = 8

def clean_workdir():
    if os.path.exists(os.environ['WORKDIR']):
        shutil.rmtree(os.environ['WORKDIR'])
        logger.warning('Workspace deleted')


def config():
    os.environ['PARALLEL'] = '1'
    os.environ['SHARDS'] = '1'
    os.environ['WORKDIR'] = './workspace'
    os.makedirs(os.environ['WORKDIR'], exist_ok=True)
    os.environ['JINA_PORT'] = '45678'

def print_result(resp):
    import io
    from base64 import b64decode
    from PIL import Image
    image_data_uri = resp.search.docs[0].matches[0].uri
    header, encoded = image_data_uri.split(",", 1)
    image_data = b64decode(encoded)
    image = Image.open(io.BytesIO(image_data))
    image.show()

def query_generator(image_paths, text_queries):
    for image_path, text in zip(image_paths, text_queries):
        doc = jina_pb2.Document()
        chunk1 = doc.chunks.add()
        chunk2 = doc.chunks.add()
        chunk1.modality = 'image'
        chunk2.modality = 'text'
        chunk1.id = uid.new_doc_id(chunk1)
        chunk2.id = uid.new_doc_id(chunk2)
        with open(image_path, 'rb') as fp:
            chunk1.buffer = fp.read()
        chunk2.text = text
        yield doc

@click.command()
@click.option('--task', '-task', type=click.Choice(['index', 'query'], case_sensitive=False))
@click.option('--data_path', '-p', default=data_path)
@click.option('--num_docs', '-n', default=num_docs)
@click.option('--batch_size', '-b', default=batch_size)
@click.option('--image_path', '-ip', default='data-all/fashion-200k/women/dresses/casual_and_day_dresses/51727804/51727804_0.jpeg')
@click.option('--text_query', '-tq', default='change color to black')
@click.option('--overwrite_workspace', '-overwrite', default=True)
def main(task, data_path, num_docs, batch_size, image_path, text_query, overwrite_workspace):
    config()
    image_paths = [image_path]
    text_queries = [text_query]
    if task == 'index':
        if overwrite_workspace:
            clean_workdir()
        f = Flow.load_config('flow-index.yml')
        with f:
            f.index_files(data_path, batch_size=batch_size, read_mode='rb', size=num_docs)        
    elif task == 'query':
        f = Flow.load_config('flow-query.yml')
        with f:
            f.search(query_generator(image_paths, text_queries), output_fn=print_result, batch_size=1)
            # f.block()

if __name__ == '__main__':
    main()
