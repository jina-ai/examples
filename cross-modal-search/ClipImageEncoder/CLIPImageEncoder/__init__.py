__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import numpy as np
import torch

from jina.executors.decorators import batching, as_ndarray
from jina.executors.encoders.frameworks import BaseTorchEncoder
from jina.executors.devices import TorchDevice

class CLIPImageEncoder(BaseTorchEncoder):
    
    def __init__(self, model_name: str ='ViT-B/32',
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = model_name

    def post_init(self):
        import clip

        assert self.model_name in clip.available_models(),\
            f'model_name={self.model_name} not in clip.available_models'

        model, _ = clip.load(self.model_name, self.device)
        self.model = model
        #self.preprocess = preprocess

    @batching
    @as_ndarray
    def encode(self, data: 'np.ndarray', *args, **kwargs) -> 'np.ndarray':

        input_torchtensor = torch.from_numpy(data.astype('float32'))
        if self.on_gpu:
            input_torchtensor = input_torchtensor.cuda()

        with torch.no_grad():
            #self.logger.warning(f'data shape {data.shape}')
            #self.logger.warning(f'data encoded shape {self.model.encode_image(input_torchtensor)}')
            embedded_data = self.model.encode_image(input_torchtensor)   

        embedded_data = embedded_data.numpy()
        return embedded_data
    

