
import os
import numpy as np
import PIL
import clip
from PIL import Image
import torch
from .. import CLIPTextEncoder

cur_dir = os.path.dirname(os.path.abspath(__file__))


def print_array_info(x, x_varname):
    print('\n')
    print(f'type({x_varname})={type(x)}')
    print(f'{x_varname}.dtype={x.dtype}')
    print(f'len({x_varname})={len(x)}')
    print(f'{x_varname}.shape={x.shape}')

def test_clip_available_models():

    models = ['ViT-B/32', 'RN50']
    for model in models:
        _,_ = clip.load(model)

def test_clip_text_encoder():

    # Input
    text = np.array(['Han likes eating pizza'])

    # Encoder embedding 
    encoder = CLIPTextEncoder()
    print_array_info(text, 'text')
    embeddeding_np = encoder.encode(text)
    print_array_info(embeddeding_np, 'embeddeding_np')

    # Compare with ouptut 
    expected = np.load(os.path.join(cur_dir, 'expected.npy'))
    np.testing.assert_almost_equal(embeddeding_np, expected)

def test_clip_text_encoder_batch():

    # Input
    text_batch = np.array(['Han likes eating pizza', 'Han likes pizza', 'Jina rocks'])

    # Encoder embedding 
    encoder = CLIPTextEncoder()
    print_array_info(text_batch, 'text_batch')
    embeddeding_batch_np = encoder.encode(text_batch)
    print_array_info(embeddeding_batch_np, 'embeddeding_batch_np')

    # Compare with ouptut 
    expected_batch = np.load(os.path.join(cur_dir, 'expected_batch.npy'))
    np.testing.assert_almost_equal(embeddeding_batch_np, expected_batch)
