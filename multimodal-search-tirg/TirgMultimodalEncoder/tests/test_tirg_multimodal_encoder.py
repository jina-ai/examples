__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os

import pytest
from PIL import Image
import torchvision
from .. import TirgMultiModalEncoder

cur_dir = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def transformer():
    return torchvision.transforms.Compose([
        torchvision.transforms.Resize(224),
        torchvision.transforms.CenterCrop(224),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize([0.485, 0.456, 0.406],
                                         [0.229, 0.224, 0.225])])


def test_multimodal_embeddings(transformer):
    imgs = []
    for img_name in range(3):
        img_path = os.path.join(cur_dir, f'imgs/{img_name}.jpeg')
        with open(img_path, 'rb') as f:
            img = Image.open(img_path)
            img = img.convert('RGB')
            img = transformer(img)
            imgs.append(img)
    img_captions = [
        'black skinny cotton twill cargo pants',
        'gray easy cargo pants',
        'white oversized cotton shirt'
    ]
    assert len(imgs) == len(img_captions)
    encoder = TirgMultiModalEncoder(
        model_path='checkpoint_fashion200k.pth',
        texts_path='texts.pkl',
        positional_modality=['image', 'text'],
        channel_axis=1,
    )
    embeddings = encoder.encode(imgs, img_captions)
    import numpy as np
    expected = np.load(os.path.join(cur_dir, 'expected.npy'))
    assert len(embeddings) == 3
    np.testing.assert_almost_equal(embeddings, expected, decimal=3)
