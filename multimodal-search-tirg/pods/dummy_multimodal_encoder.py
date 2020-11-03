__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import List

import numpy as np

from jina.executors.decorators import batching, as_ndarray
from jina.executors.encoders.multimodal import BaseMultiModalEncoder
from jina.proto import jina_pb2

class DummyMultimodalEncoder(BaseMultiModalEncoder):

    def __init__(self, emb_dim=1, 
                 positional_modality: List[str] = ['image', 'text'], 
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.emb_dim = emb_dim
        self.positional_modality = positional_modality

    @batching
    @as_ndarray
    def encode(self, data: 'np.ndarray', *args, **kwargs) -> 'np.ndarray':
        a = data[self.positional_modality.index('image')]
        self.logger.info(f'>>> {type(a)}')
        b = data[self.positional_modality.index('text')]
        self.logger.info(f'>>> {b}')
        assert isinstance(data[self.positional_modality.index('image')], jina_pb2.NdArray)
        assert isinstance(data[self.positional_modality.index('text')][0], str)
        _feature = np.random.rand(data[0].shape[0], self.emb_dim)
        return _feature