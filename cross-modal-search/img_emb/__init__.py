__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import torch
import numpy as np
from torch.autograd import Variable
# model is a file from the vsepp github
import sys

sys.path.append(".")
from model import VSE

from jina.executors.decorators import batching, as_ndarray
from jina.executors.encoders.frameworks import BaseTorchEncoder


class VSEImageEncoder(BaseTorchEncoder):
    """
    :class:`VSEImageEncoder` encodes data from a ndarray, potentially B x (Channel x Height x Width) into a
        ndarray of `B x D`. using VSE img_emb branch

    """

    def __init__(self, path: str = 'runs/f30k_vse++_vggfull/model_best.pth.tar',
                 pool_strategy: str = 'mean', channel_axis: int = 1, *args, **kwargs):
        """
        :path : path where to find the model.pth file
        """
        super().__init__(*args, **kwargs)
        self.path = path
        self.pool_strategy = pool_strategy
        self.channel_axis = channel_axis
        self._default_channel_axis = 1

    def post_init(self):
        if self.pool_strategy is not None:
            self.pool_fn = getattr(np, self.pool_strategy)

        checkpoint = torch.load(self.path,
                                map_location=torch.device('cpu' if not self.on_gpu else 'cuda'))
        opt = checkpoint['opt']

        model = VSE(opt)
        model.load_state_dict(checkpoint['model'])
        model.img_enc.eval()
        self.model = model.img_enc
        self.to_device(self.model)
        del model.txt_enc

    def _get_features(self, data):
        # It needs Resize and Normalization before reaching this Point in another Pod
        # Check how this works, it may not be necessary to squeeze
        images = Variable(data, requires_grad=False)
        img_emb = self.model(images)
        return img_emb

    def _get_pooling(self, feature_map: 'np.ndarray') -> 'np.ndarray':
        if feature_map.ndim == 2 or self.pool_strategy is None:
            return feature_map
        return self.pool_fn(feature_map, axis=(2, 3))

    @batching
    @as_ndarray
    def encode(self, data: 'np.ndarray', *args, **kwargs) -> 'np.ndarray':
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
        return self._get_pooling(_feature)
