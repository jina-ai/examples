__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import numpy as np

from jina.executors.decorators import batching, as_ndarray
from jina.executors.encoders.multimodal import BaseMultiModalEncoder


class DummyMultiModalEncoder(BaseMultiModalEncoder):

    def __init__(self, emb_dim=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.emb_dim = emb_dim
        self.positional_modality = ['image', 'text']

    @batching
    @as_ndarray
    def encode(self, *data: 'np.ndarray', **kwargs) -> 'np.ndarray':
        """
        :param: data: M arguments of shape `B x (D)` numpy ``ndarray``, `B` is the size of the batch,
        `M` is the number of modalities
        :return: a `B x D` numpy ``ndarray``
        """
        assert isinstance(data[self.positional_modality.index('image')][0], float)
        assert isinstance(data[self.positional_modality.index('text')][0], str)
        _feature = np.random.rand(data[0].shape[0], self.emb_dim)
        return _feature
