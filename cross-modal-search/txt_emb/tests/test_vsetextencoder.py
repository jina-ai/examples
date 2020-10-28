__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import numpy as np
from .. import VSETextEncoder

cur_dir = os.path.dirname(os.path.abspath(__file__))


def test_text_embedding():
    encoder = VSETextEncoder()
    text = np.array(['the man with pierced ears is wearing glasses and an orange hat.',
                     'a man with glasses is wearing a beer can crocheted hat.',
                     'a man in an orange hat starring at something.',
                     'a man with gauges and glasses is wearing a blitz hat.',
                     'a man wears an orange hat and glasses.'])

    embedding = encoder.encode(text)
    expected = np.load(os.path.join(cur_dir, 'expected.npy'))

    assert embedding.shape == (5, 1024)
    np.testing.assert_almost_equal(embedding, expected)

    for i in range(len(text)):
        single_embedding = encoder.encode([text[i]])[0]
        np.testing.assert_almost_equal(single_embedding, embedding[i])
