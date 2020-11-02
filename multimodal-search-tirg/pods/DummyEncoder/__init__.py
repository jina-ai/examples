__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import numpy as np

from jina.executors.decorators import batching, as_ndarray
from jina.executors.encoders import BaseEncoder


class DummyEncoder(BaseEncoder):

    def __init__(self, emb_dim=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.emb_dim = emb_dim

    @batching
    @as_ndarray
    def encode(self, data: 'np.ndarray', *args, **kwargs) -> 'np.ndarray':
        _feature = np.random.rand(data.shape[0], self.emb_dim)
        return _feature