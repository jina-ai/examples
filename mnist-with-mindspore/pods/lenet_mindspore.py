from jina.executors.encoders.frameworks import BaseMindsporeEncoder

import sys
sys.path.append('..')

from lenet import *


class LeNetImageEncoder(BaseMindsporeEncoder):
    def encode(self, data, *args, **kwargs):
        from mindspore import Tensor
        return self.model(Tensor(data.astype('float32'))).asnumpy()

    def get_model(self):
        return LeNet5()
