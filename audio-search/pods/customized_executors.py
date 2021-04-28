__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import io
from typing import Any, Dict, List

import numpy as np
from jina.executors.decorators import batching, single
from jina.executors.encoders.frameworks import BaseTFEncoder
from jina.executors.segmenters import BaseSegmenter
from jinahub.vggish_input import *
from jinahub.vggish_params import *
from jinahub.vggish_postprocess import *
from jinahub.vggish_slim import *


class VggishEncoder(BaseTFEncoder):
    def __init__(self, model_path: str, pca_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_path = model_path
        self.pca_path = pca_path

    def post_init(self):
        self.to_device()
        import tensorflow as tf
        tf.compat.v1.disable_eager_execution()
        self.sess = tf.compat.v1.Session()
        define_vggish_slim()
        load_vggish_slim_checkpoint(self.sess, self.model_path)
        self.feature_tensor = self.sess.graph.get_tensor_by_name(
            INPUT_TENSOR_NAME)
        self.embedding_tensor = self.sess.graph.get_tensor_by_name(
            OUTPUT_TENSOR_NAME)
        self.post_processor = Postprocessor(self.pca_path)

    @batching
    def encode(self, content: Any, *args, **kwargs) -> Any:
        [embedding_batch] = self.sess.run([self.embedding_tensor],
                                          feed_dict={self.feature_tensor: content})
        result = self.post_processor.postprocess(embedding_batch)
        return (np.float32(result) - 128.) / 128.


class VggishSegmenter(BaseSegmenter):
    def __init__(self, window_length_secs=0.025, hop_length_secs=0.010, *args, **kwargs):
        """
        :param frame_length: the number of samples in each frame
        :param hop_length: number of samples to advance between frames
        """
        super().__init__(*args, **kwargs)
        self.window_length_secs = window_length_secs
        self.hop_length_secs = hop_length_secs

    @single(slice_nargs=2, flatten_output=False)
    def segment(self, uri, buffer, *args, **kwargs) -> List[Dict]:
        result = []
        # load the data
        data, sample_rate = self.read_wav(uri, buffer)
        if data is None:
            return result
        # slice the wav array
        mel_data = self.wav2mel(data, sample_rate)
        for idx, blob in enumerate(mel_data):
            self.logger.debug(f'blob: {blob.shape}')
            result.append(dict(offset=idx, weight=1.0, blob=blob))
        return result

    def wav2mel(self, blob, sample_rate):
        self.logger.debug(f'blob: {blob.shape}, sample_rate: {sample_rate}')
        mel_spec = waveform_to_examples(blob, sample_rate).squeeze()
        self.logger.debug(f'mel_spec: {mel_spec.shape}')
        return mel_spec

    def read_wav(self, uri, buffer):
        import soundfile as sf
        wav_data = None
        sample_rate = None
        if buffer:
            wav_data, sample_rate = sf.read(io.BytesIO(buffer), dtype='int16')
        elif uri:
            wav_data, sample_rate = sf.read(uri, dtype='int16')
        else:
            return None, None
        self.logger.debug(f'sample_rate: {sample_rate}')
        if len(wav_data.shape) > 1:
            wav_data = np.mean(wav_data, axis=1)
        data = wav_data / 32768.0
        return data, sample_rate
