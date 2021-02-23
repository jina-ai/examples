
import os

import numpy as np
import clip
import PIL
import torch
import pytest

from .. import CLIPImageEncoder

cur_dir = os.path.dirname(os.path.abspath(__file__))

def print_array_info(x, x_varname):
    print('\n')
    print(f'type({x_varname})={type(x)}')
    print(f'{x_varname}.dtype={x.dtype}')
    print(f'len({x_varname})={len(x)}')
    print(f'{x_varname}.shape={x.shape}')


def test_clip_available_models():

    models = ['ViT-B/32', 'RN50']
    for model_name in models:
        m = CLIPImageEncoder(model_name=model_name)
        assert m.model_name == model_name

def test_inexistant_model():
    with pytest.raises(AssertionError):
       encoder = CLIPImageEncoder(model_name='model_name_inexistant')


def test_clip_image_encoder():

    # Input
    man_piercing_image_path = os.path.join(cur_dir, '../imgs/man_piercing.jpg')
    im = PIL.Image.open(man_piercing_image_path)
    _, preprocess = clip.load('ViT-B/32')
    im_tensor_clip_input = preprocess(im).unsqueeze(0)
    im_tensor_clip_np = im_tensor_clip_input.detach().numpy()

    # Encoder embedding 
    encoder = CLIPImageEncoder()
    print_array_info(im_tensor_clip_np, 'im_tensor_clip_np')
    embeddeding_np = encoder.encode(im_tensor_clip_np)
    print_array_info(embeddeding_np, 'embeddeding_np')

    # Compare with ouptut 
    expected = np.load(os.path.join(cur_dir, 'expected.npy'))
    np.testing.assert_almost_equal(embeddeding_np, expected, decimal=3)


def test_clip_image_encoder_batch():

    # Input
    man_piercing_image_path = os.path.join(cur_dir, '../imgs/man_piercing.jpg')
    im = PIL.Image.open(man_piercing_image_path)
    _, preprocess = clip.load('ViT-B/32')
    im_tensor_clip_input = preprocess(im).unsqueeze(0)
    im_tensor_clip_np = im_tensor_clip_input.detach().numpy()
    batch = np.vstack([im_tensor_clip_input, im_tensor_clip_input, im_tensor_clip_input])

    # Encoder embedding 
    encoder = CLIPImageEncoder()
    print_array_info(batch, 'batch')
    embeddeding_batch_np = encoder.encode(batch)
    print_array_info(embeddeding_batch_np, 'embeddeding_batch_np')

    # Compare with ouptut 
    expected = np.load(os.path.join(cur_dir, 'expected_batch.npy'))
    np.testing.assert_almost_equal(embeddeding_batch_np, expected, decimal=3)


