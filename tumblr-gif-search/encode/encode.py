import numpy as np
import tensorflow as tf
from jina.executors.decorators import batching, as_ndarray
from jina.executors.encoders import BaseImageEncoder


class TF2ImageEncoder(BaseImageEncoder):
    batch_size = 128

    def __init__(self,
                 model_name: str,
                 pool_strategy: str = 'avg',
                 img_shape: int = 96,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.img_shape = img_shape
        self.pool_strategy = pool_strategy
        self.model_name = model_name

    def post_init(self):
        # https://keras.io/applications/
        # weights can be only None or 'imagenet'
        model = getattr(tf.keras.applications, self.model_name)(
            input_shape=(self.img_shape, self.img_shape, 3),
            include_top=False,
            pooling=self.pool_strategy,
            weights='imagenet')

        model.trainable = False
        self.model = model

    @batching
    @as_ndarray
    def encode(self, img: 'np.ndarray', *args, **kwargs) -> np.ndarray:
        return self.model(img)
