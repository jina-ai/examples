__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import click
import os
from jina.flow import Flow
from jina.proto import jina_pb2

RANDOM_SEED = 14

cur_dir = os.path.dirname(os.path.abspath(__file__))


def config():
    os.environ['PARALLEL'] = str(1)
    os.environ['SHARDS'] = str(1)
    os.environ['COLOR_CHANNEL_AXIS'] = str(0)
    os.environ['JINA_PORT'] = str(45678)


def input_index_data(num_docs=None, batch_size=8):
    from dataset import get_data_loader
    data_loader = get_data_loader(root=os.path.join(cur_dir, 'data/f30k/images'),
                                  json=os.path.join(cur_dir, 'data/f30k/dataset_flickr30k.json'),
                                  split='test',
                                  batch_size=batch_size)
    for i, (images, captions) in enumerate(data_loader):
        for image in images:
            document = jina_pb2.Document()
            document.buffer = image
            document.modality = 'image'
            yield document

        for caption in captions:
            document = jina_pb2.Document()
            document.text = caption
            document.modality = 'text'
            yield document

        if num_docs and (i + 1) * batch_size >= num_docs:
            break


def input_search_text_data(text):
    document = jina_pb2.Document()
    document.text = text
    document.modality = 'text'
    return [document]


def input_search_image_file(image_file_path):
    with open(image_file_path, 'rb') as fp:
        image_buffer = fp.read()
    document = jina_pb2.Document()
    document.buffer = image_buffer
    document.modality = 'image'
    return [document]


def show_top_k(resp, text):
    for d in resp.search.docs:
        print(f'Ta-Dah🔮, here are what we found for caption: {text}')
        for idx, match in enumerate(d.matches):
            score = match.score.value
            if score < 0.0:
                continue
            print(f'match {match}')


def print_top_k(resp, img):
    for d in resp.search.docs:
        print(f'Ta-Dah🔮, here are what we found for image: {img}')
        for idx, match in enumerate(d.matches):
            score = match.score.value
            if score < 0.0:
                continue
            print(f'match {match}')


@click.command()
@click.option('--task', '-t')
@click.option('--num_docs', '-n', default=50)
@click.option('--batch_size', '-b', default=16)
@click.option('--top_k', '-k', default=5)
def main(task, num_docs, batch_size, top_k):
    config()
    if task == 'index':
        f = Flow().load_config('flow-index.yml')
        with f:
            f.index(input_fn=input_index_data(num_docs, batch_size), batch_size=batch_size)
    elif task == 'query-t2i':
        f = Flow().load_config('flow-query.yml')
        with f:
            while True:
                text = input('please type a caption to search an image from: ')
                if not text:
                    break
                f.search(input_fn=input_search_text_data(text),
                         output_fn=lambda x: show_top_k(x, text), top_k=top_k)
    elif task == 'query-i2t':
        f = Flow().load_config('flow-query.yml')
        with f:
            while True:
                image_file_path = input('please type an image file path to search for a caption: ')
                if not image_file_path:
                    break
                f.search(input_fn=input_search_image_file(image_file_path),
                         output_fn=lambda x: print_top_k(x, text), top_k=top_k)
    elif task == 'query-restful':
        # not working, missing a way to send modality via REST API
        f = Flow().load_config('flow-query.yml')
        f.use_rest_gateway()
        with f:
            f.block()
    else:
        raise NotImplementedError(f'unknown task: {task}.'
                                  f' A valid task is either `index`, `query-restful`, `query-i2t` and `query-t2i`.')


if __name__ == '__main__':
    main()
