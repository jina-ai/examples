
import os
import numpy as np
import PIL
import clip
from PIL import Image
import torch
from .. import CLIPImageEncoder

cur_dir = os.path.dirname(os.path.abspath(__file__))


def test_clip_available_models():

    models = ['ViT-B/32', 'RN50']
    for model in models:
        _,_ = clip.load(model)


def test_clip_image_encoder():

    man_piercing_image_path = os.path.join(cur_dir, 'imgs/man_piercing.jpg')
    im = PIL.Image.open(man_piercing_image_path)
    
    device='cpu'
    _, preprocess = clip.load('ViT-B/32', device=device)
    im_tensor_clip_input = preprocess(im).unsqueeze(0).to(device)
    im_tensor_clip_np = im_tensor_clip_input.detach().numpy()

    encoder = CLIPImageEncoder()
    embeddeding_np = encoder.encode(im_tensor_clip_np)
    expected = np.load(os.path.join(cur_dir, 'expected.npy'))
    np.testing.assert_almost_equal(embeddeding_np, expected)
