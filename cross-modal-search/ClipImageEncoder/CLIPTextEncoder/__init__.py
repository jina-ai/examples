__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import numpy as np
from jina.executors.decorators import batching, as_ndarray
from jina.executors.encoders.frameworks import BaseTorchEncoder
from jina.executors.devices import TorchDevice
import torch
import clip

class CLIPTextEncoder(BaseTorchEncoder, TorchDevice):
    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post_init(self):
        import clip
        device = "cuda" if self.on_gpu else "cpu"
        model, preprocess = clip.load('ViT-B/32', device)
        self.model = model
        self.preprocess = preprocess

    @batching
    @as_ndarray
    def encode(self, text: str, *args, **kwargs) -> 'np.ndarray':
        # data.shape should be [1, 3, 224, 224]
        with torch.no_grad():
            return self.model.encode_text(clip.tokenize(text))
    


