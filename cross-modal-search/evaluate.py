__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os

import click

from jina import Flow
from jina import Document

cur_dir = os.path.dirname(os.path.abspath(__file__))


def config(model_name):
    os.environ['JINA_PARALLEL'] = os.environ.get('JINA_PARALLEL', '1')
    os.environ['JINA_SHARDS'] = os.environ.get('JINA_SHARDS', '1')
    os.environ['JINA_PORT'] = '45678'
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


def input_index_data(num_docs=None, batch_size=8, dataset_type='f30k'):
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
            current_hash = hash(image)
            with Document() as document_img:
                document_img.buffer = image
                document_img.modality = 'image'
                document_img.mime_type = 'image/jpeg'
                document_img.tags['id'] = current_hash

            with Document() as document_caption:
                document_caption.text = caption
                document_caption.modality = 'text'
                document_caption.mime_type = 'text/plain'
                document_caption.tags['id'] = caption
            yield document_img, document_caption

        if num_docs and (i + 1) * batch_size >= num_docs:
            break


def evaluation_generator(num_docs=None, batch_size=8, dataset_type='f8k'):
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
            with Document() as document:
                document.text = caption
                document.modality = 'text'
                document.mime_type = 'text/plain'
            with Document() as gt:
                match = Document()
                match.tags['id'] = hash(image)
                gt.matches.append(match)
            yield document, gt

        if num_docs and (i + 1) * batch_size >= num_docs:
            break


def print_evaluation_score(resp):
    print("==================================")
    print(len(resp.search.docs))
    for doc in resp.search.docs:
       print(doc.id)
       print(doc.evaluations)
       print(len(doc.evaluations))
       print(f' Evaluation {doc.evaluations[0].op_name}: {doc.evaluations[0].value}')
    print("==================================")


@click.command()
@click.option('--num_docs', '-n', default=50)
@click.option('--request_size', '-s', default=16)
@click.option('--data_set', '-d', type=click.Choice(['f30k', 'f8k'], case_sensitive=False), default='f8k')
@click.option('--model_name', '-m', type=click.Choice(['clip', 'vse'], case_sensitive=False), default='clip')
def main(num_docs, request_size, data_set, model_name):
    config(model_name)
    with Flow().load_config('flow-index.yml') as f:
        f.index(
            input_fn=input_index_data(num_docs, request_size, data_set),
            request_size=request_size
        )
    with Flow().load_config('flow-query.yml').add(name='evaluator', uses='yaml/evaluate.yml') as flow_eval:
        flow_eval.search(input_fn=evaluation_generator, on_done=print_evaluation_score)


if __name__ == '__main__':
    main()
