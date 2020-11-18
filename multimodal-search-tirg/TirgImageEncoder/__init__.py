__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import sys
import pickle

from jina.executors.decorators import batching, as_ndarray
from jina.executors.encoders.frameworks import BaseTorchEncoder
from jina.excepts import PretrainedModelFileDoesNotExist

sys.path.append(".")
from img_text_composition_models import TIRG


class TirgImageEncoder(BaseTorchEncoder):

    def __init__(self, model_path: str = 'checkpoint.pth',
                 texts_path: str = 'texts.pkl',
                 channel_axis: int = -1, 
                 *args, **kwargs):
        """
        :param model_path: the path where the model is stored.
        """
        super().__init__(*args, **kwargs)
        self.model_path = model_path
        self.texts_path = texts_path
        self.channel_axis = channel_axis
        # axis 0 is the batch
        self._default_channel_axis = 1

    def post_init(self):
        super().post_init()
        import torch
        if self.model_path and os.path.exists(self.model_path):
            with open (self.texts_path, 'rb') as fp:
                texts = pickle.load(fp)
            self.model = TIRG(texts, 512)
            model_sd = torch.load(self.model_path, map_location=torch.device('cpu'))
            self.model.load_state_dict(model_sd['model_state_dict'])
            self.model.eval()
            self.to_device(self.model)
        else:
            raise PretrainedModelFileDoesNotExist(f'model {self.model_path} does not exist')

    def _get_features(self, data):
        return self.model.extract_img_feature(data)

    @batching
    @as_ndarray
    def encode(self, data: 'np.ndarray', *args, **kwargs) -> 'np.ndarray':
        import numpy as np
        if self.channel_axis != self._default_channel_axis:
            data = np.moveaxis(data, self.channel_axis, self._default_channel_axis)
        import torch
        _input = torch.from_numpy(data.astype('float32'))
        if self.on_gpu:
            _input = _input.cuda()
        _feature = self._get_features(_input).detach()
        if self.on_gpu:
            _feature = _feature.cpu()
        _feature = _feature.numpy()
        return _feature