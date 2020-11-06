__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
from PIL import Image
from torchvision import transforms
from .. import VSEImageEncoder

cur_dir = os.path.dirname(os.path.abspath(__file__))


def test_man_piercing_embedding():
    man_piercing_image_path = os.path.join(cur_dir, 'imgs/man_piercing.jpg')
    img = Image.open(man_piercing_image_path).convert('RGB')

    transformer = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    image = transformer(img)
    encoder = VSEImageEncoder()

    embedding = encoder.encode(image.unsqueeze(0).numpy())
    import numpy as np
    expected = np.load(os.path.join(cur_dir, 'expected.npy'))
    assert embedding.shape == (1, 1024)
    np.testing.assert_almost_equal(embedding, expected)
