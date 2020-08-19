from jina.executors.encoders.frameworks import BaseMindsporeEncoder
from jina.executors.crafters.image.io import ImageReader
from jina.drivers.helper import pb2array

import sys
sys.path.append('..')

import numpy as np

from lenet import *


class LeNetImageEncoder(BaseMindsporeEncoder):
    def encode(self, data, *args, **kwargs):
        from mindspore import Tensor
        return self.model(Tensor(data.astype('float32'))).asnumpy()

    def get_model(self):
        return LeNet5()


class MnistImageReader(ImageReader):
    def craft(self, buffer, *args, **kwargs):
        result = []
        # convert buffer to blob
        array = pb2array(buffer)
        for img in array:
            _img = img.reshape(28, 28)
            result.append(np.extend_dims(_img, axis=0))
        return dict(weight=1., blob=np.array(result))

