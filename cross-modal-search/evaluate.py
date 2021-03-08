__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import hashlib

import click
from jina import Flow
from jina import Document

from dataset import input_index_data

cur_dir = os.path.dirname(os.path.abspath(__file__))
sum_of_score = 0
num_of_searches = 0


def config(model_name):
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '1')
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_SHARDS', '1')
    os.environ['JINA_PORT'] = '45678'
    os.environ['JINA_USE_REST_API'] = 'false'
    if model_name == 'clip':
        os.environ['JINA_IMAGE_ENCODER'] = 'docker://jinahub/pod.encoder.clipimageencoder:0.0.1-1.0.7'
        os.environ['JINA_TEXT_ENCODER'] = 'docker://jinahub/pod.encoder.cliptextencoder:0.0.1-1.0.7'
        os.environ['JINA_TEXT_ENCODER_INTERNAL'] = 'yaml/clip/text-encoder.yml'
    elif model_name == 'vse':
        os.environ['JINA_IMAGE_ENCODER'] = 'docker://jinahub/pod.encoder.vseimageencoder:0.0.5-1.0.7'
        os.environ['JINA_TEXT_ENCODER'] = 'docker://jinahub/pod.encoder.vsetextencoder:0.0.6-1.0.7'
        os.environ['JINA_TEXT_ENCODER_INTERNAL'] = 'yaml/vse/text-encoder.yml'
    else:
        msg = f'Unsupported model {model_name}.'
        msg += 'Expected `clip` or `vse`.'
        raise ValueError(msg)


def evaluation_generator(num_docs=None, batch_size=8, dataset_type='f8k', mode='text2image'):
    from dataset import get_data_loader
    captions = 'dataset_flickr30k.json' if dataset_type == 'f30k' else 'captions.txt'
    data_loader = get_data_loader(
        root=os.path.join(cur_dir, f'data/{dataset_type}/images'),
        captions=os.path.join(cur_dir, f'data/{dataset_type}/{captions}'),
        split='test',
        batch_size=batch_size,
        dataset_type=dataset_type
    )
    for i, (images, captions) in enumerate(data_loader):
        for image, caption in zip(images, captions):
            hashed = hashlib.sha1(image).hexdigest()
            if mode == 'text2image':
                with Document() as document:
                    document.text = caption
                    document.modality = 'text'
                    document.mime_type = 'text/plain'
                with Document() as gt:
                    match = Document()
                    match.tags['id'] = hashed
                    gt.matches.append(match)
                yield document, gt
            elif mode == 'image2text':
                with Document() as document:
                    document.buffer = image
                    document.modality = 'image'
                    document.mime_type = 'image/jpeg'
                    document.convert_buffer_to_uri()
                with Document() as gt:
                    match = Document()
                    match.tags['id'] = caption
                    gt.matches.append(match)
                yield document, gt
            else:
                msg = f'Not supported mode {mode}.'
                msg += 'expected `image2text` or `text2image`'
                raise ValueError(msg)

        if num_docs and (i + 1) * batch_size >= num_docs:
            break


def print_evaluation_score(resp):
    batch_of_score = 0
    for doc in resp.search.docs:
        batch_of_score += doc.evaluations[0].value
    global sum_of_score
    global num_of_searches
    sum_of_score += batch_of_score
    num_of_searches += len(resp.search.docs)


@click.command()
@click.option('--index_num_docs', '-i', default=50)
@click.option('--evaluate_num_docs', '-n', default=20)
@click.option('--request_size', '-s', default=8)
@click.option('--data_set', '-d', type=click.Choice(['f30k', 'f8k'], case_sensitive=False), default='f8k')
@click.option('--model_name', '-m', type=click.Choice(['clip', 'vse'], case_sensitive=False), default='clip')
@click.option('--evaluation_mode', '-e', type=click.Choice(['image2text', 'text2image'], case_sensitive=False),
              default='text2image')
def main(index_num_docs, evaluate_num_docs, request_size, data_set, model_name, evaluation_mode):
    config(model_name)
    if index_num_docs > 0:
        with Flow.load_config('flow-index.yml') as f:
            f.index(
                input_fn=input_index_data(index_num_docs, request_size, data_set),
                request_size=request_size
            )
    with Flow.load_config('flow-query.yml').add(name='evaluator', uses='yaml/evaluate.yml') as flow_eval:
        flow_eval.search(
            input_fn=evaluation_generator(evaluate_num_docs, request_size, data_set, mode=evaluation_mode),
            on_done=print_evaluation_score
        )
    print(f'MeanReciprocalRank is: {sum_of_score / num_of_searches}')


if __name__ == '__main__':
    main()
