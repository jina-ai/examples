import numpy as np
from typing import Any, List, Dict

from jina.executors.encoders import BaseEncoder
from jina.executors.encoders.frameworks import BaseTFEncoder
from jina.executors.decorators import batching
from jina.executors.crafters import BaseSegmenter, BaseCrafter
import vggish

class DummyEncoder(BaseEncoder):
    @batching
    def encode(self, data: Any, *args, **kwargs) -> Any:
        """
        Copy the data into the embedding
        :param data:
        :return:
        """
        assert isinstance(data, np.ndarray)
        if data.ndim != 2:
            self.logger.info(f'data.shape: {data.shape}')
            raise ValueError
        assert data.shape[1] == 128
        return data


class NdArraySegmentor(BaseSegmenter):
    required_keys = {'blob', }

    def craft(self, blob, *args, **kwargs) -> List[Dict]:
        num_chunks = blob.shape[0]
        assert num_chunks == 10
        return [dict(
            offset=idx, weight=1.0, blob=frame_emb, length=num_chunks) for idx, frame_emb in enumerate(blob)]


class Wav2LogMelSpectrogram(BaseCrafter):
    required_keys = {'blob', }

    def __init__(self, sample_rate: int=44100, *args, **kwargs):
        super(Wav2LogMelSpectrogram, self).__init__()
        self.sample_rate = sample_rate

    def craft(self, blob, *args, **kwargs) -> Dict:
        mel_spec = vggish.vggish_input.waveform_to_examples(blob, self.sample_rate)
        return dict(blob=mel_spec)


class VggishEncoder(BaseTFEncoder):
    def __init__(self, model_path: str, pca_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_path = model_path
        self.pca_path = pca_path

    def post_init(self):
        self.to_device()
        import tensorflow as tf
        self.sess = tf.Session()
        vggish.vggish_slim.define_vggish_slim()
        vggish.vggish_slim.load_vggish_slim_checkpoint(self.sess, self.model_path)
        self.feature_tensor = self.sess.graph.get_tensor_by_name(
            vggish.vggish_params.INPUT_TENSOR_NAME)
        self.embedding_tensor = self.sess.graph.get_tensor_by_name(
            vggish.vggish_params.OUTPUT_TENSOR_NAME)
        self.post_processor = vggish.vggish_postprocess.Postprocessor(self.pca_path)

    @batching
    def encode(self, data: Any, *args, **kwargs) -> Any:
        [embedding_batch] = self.sess.run([self.embedding_tensor],
                                          feed_dict={self.embedding_tensor: data})
        result = self.post_processor.postprocess(embedding_batch)
        return result
