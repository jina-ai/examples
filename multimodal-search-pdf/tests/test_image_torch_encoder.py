# test image_encoder.py
import pytest
from PIL import Image
import numpy as np
from jina import Document, DocumentArray

from pods.image_encoder import ImageTorchEncoder


@pytest.fixture()
def image_uri() -> str:
    return '../toy_data/photo-1.png'


@pytest.fixture()
def image_arr(image_uri: str) -> 'np.ndarray':
    raw_img = Image.open(image_uri)
    raw_img = raw_img.convert('RGB')
    return np.array(raw_img).astype('float32')


def test_image_torch_encoder_computes_embeds(
    image_uri: str,
    image_arr: 'np.ndarray'
):
    encoder = ImageTorchEncoder(channel_axis=3)
    docs = DocumentArray([
        Document(uri=image_uri, mime_type='image/png', chunks=[Document(content=image_arr)]),
        Document(uri=image_uri, mime_type='image/png', chunks=[Document(content=image_arr)]),
        Document(uri=image_uri, mime_type='image/png', chunks=[Document(content=image_arr)])
    ])

    encoder.encode(docs)

    for doc in docs.traverse_flat(['c']):
        assert doc.embedding is not None
        assert doc.embedding.shape == (1280, )
