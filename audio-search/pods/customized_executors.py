import numpy as np
import io
from typing import Any, Dict, List

from jina.executors.encoders.frameworks import BaseTFEncoder
from jina.executors.decorators import batching
from jina.executors.crafters import BaseCrafter, BaseSegmenter

import vggish_params
import vggish_input
import vggish_slim
import vggish_postprocess
import librosa


class Wav2LogMelSpectrogram(BaseCrafter):
    required_keys = {'blob', 'meta_info'}

    def __init__(self, *args, **kwargs):
        super(Wav2LogMelSpectrogram, self).__init__()

    def craft(self, blob, meta_info, *args, **kwargs) -> Dict:
        sample_rate = int.from_bytes(meta_info, byteorder='big')
        self.logger.debug(f'blob: {blob.shape}, sample_rate: {sample_rate}')
        mel_spec = vggish_input.waveform_to_examples(blob, sample_rate)
        self.logger.debug(f'mel_spec: {mel_spec.shape}')
        return dict(blob=mel_spec.squeeze())


class VggishEncoder(BaseTFEncoder):
    def __init__(self, model_path: str, pca_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.info('init vggishencoder')
        self.model_path = model_path
        self.pca_path = pca_path

    def post_init(self):
        self.to_device()
        import tensorflow as tf
        tf.compat.v1.disable_eager_execution()
        self.sess = tf.compat.v1.Session()
        vggish_slim.define_vggish_slim()
        vggish_slim.load_vggish_slim_checkpoint(self.sess, self.model_path)
        self.feature_tensor = self.sess.graph.get_tensor_by_name(
            vggish_params.INPUT_TENSOR_NAME)
        self.embedding_tensor = self.sess.graph.get_tensor_by_name(
            vggish_params.OUTPUT_TENSOR_NAME)
        self.post_processor = vggish_postprocess.Postprocessor(self.pca_path)

    @batching
    def encode(self, data: Any, *args, **kwargs) -> Any:
        [embedding_batch] = self.sess.run([self.embedding_tensor],
                                          feed_dict={self.feature_tensor: data})
        result = self.post_processor.postprocess(embedding_batch)
        return (np.float32(result) - 128.) / 128.


class VggishAudioReader(BaseCrafter):
    def craft(self, uri, buffer, *args, **kwargs) -> Dict:
        import soundfile as sf
        wav_data = None
        sample_rate = None
        if buffer:
            wav_data, sample_rate = sf.read(io.BytesIO(buffer), dtype='int16')
        elif uri:
            wav_data, sample_rate = sf.read(uri, dtype='int16')
        else:
            return dict()
        self.logger.debug(f'sample_rate: {sample_rate}')
        if len(wav_data.shape) > 1:
            wav_data = np.mean(wav_data, axis=1)
        data = wav_data / 32768.0
        self.logger.info(f'blob: {data.shape}')
        return dict(weight=1., blob=data, meta_info=sample_rate.to_bytes(length=16, byteorder='big'))


class VggishCrafter(BaseSegmenter):
    def __init__(self, window_length_secs=0.025, hop_length_secs=0.010, *args, **kwargs):
        """
        :param frame_length: the number of samples in each frame
        :param hop_length: number of samples to advance between frames
        """
        super().__init__(*args, **kwargs)
        self.window_length_secs = window_length_secs
        self.hop_length_secs = hop_length_secs

    def craft(self, uri, buffer, *args, **kwargs) -> List[Dict]:
        result = []
        # load the data
        self.logger.info('loading data ...')
        data, sample_rate = self.read_wav(uri, buffer)
        if data is None:
            return result
        # slice the wav array
        self.logger.info('segmenting data')
        mel_data = self.wav2mel(data, sample_rate)
        for idx, blob in enumerate(mel_data):
            self.logger.info(f'blob: {blob.shape}')
            result.append(dict(offset=idx, weight=1.0, blob=blob, length=mel_data.shape[0]))

        # frames = self.segment(data, sample_rate)
        # # convert to mel
        # self.logger.info(f'converting data into mel: {frames.shape[0]}')
        # for idx, frame in enumerate(frames):
        #     blob = self.wav2mel(frame, sample_rate)
        #     result.append(dict(offset=idx, weight=1.0, blob=blob, length=frames.shape[0]))
        return result

    def wav2mel(self, blob, sample_rate):
        self.logger.debug(f'blob: {blob.shape}, sample_rate: {sample_rate}')
        mel_spec = vggish_input.waveform_to_examples(blob, sample_rate).squeeze()
        self.logger.info(f'mel_spec: {mel_spec.shape}')
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

    def segment(self, signal, sample_rate):
        frame_length = int(round(sample_rate * self.window_length_secs))
        hop_length = int(round(sample_rate * self.hop_length_secs))
        if signal.ndim == 1:  # mono
            frames = librosa.util.frame(signal, frame_length=frame_length, hop_length=hop_length, axis=0)
        elif signal.ndim == 2:  # stereo
            left_frames = librosa.util.frame(
                signal[0,], frame_length=frame_length, hop_length=hop_length, axis=0)
            right_frames = librosa.util.frame(
                signal[1,], frame_length=frame_length, hop_length=hop_length, axis=0)
            frames = np.concatenate((left_frames, right_frames), axis=0)
        else:
            raise ValueError(f'audio signal must be 1D or 2D array: {signal}')
        return frames
