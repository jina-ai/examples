__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from jina.executors.encoders import BaseNumericEncoder


class MyEncoder(BaseNumericEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def encode(self, data: 'np.ndarray', *args, **kwargs):
        return data