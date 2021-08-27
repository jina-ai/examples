import os
from typing import Tuple, Dict, Optional

import torch
import numpy as np
import librosa as lr
import torchaudio
from jina import Executor, DocumentArray, requests, Document
from jina_commons import get_logger

from vggish.vggish_input import waveform_to_examples
from vggish.vggish_params import SAMPLE_RATE


class Wav2MelCrafter(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self)

    @requests
    def segment(self, docs: Optional[DocumentArray] = None, **kwargs):
        if not docs:
            return
        for doc in docs:
            result_chunk = []
            for chunk in doc.chunks:
                mel_data = waveform_to_examples(chunk.blob, chunk.tags['sample_rate'])
                if mel_data.ndim != 3:
                    self.logger.warning(
                        f'failed to convert from wave to mel, chunk.blob: {chunk.blob.shape}, sample_rate: {SAMPLE_RATE}'
                    )
                    continue
                if mel_data.shape[0] <= 0:
                    self.logger.warning(
                        f'chunk between {chunk.location} is skipped due to the duration is too short'
                    )
                if mel_data.ndim == 2:
                    mel_data = np.atleast_3d(mel_data)
                    mel_data = mel_data.reshape(1, mel_data.shape[0], mel_data.shape[1])
                chunk.blob = mel_data
                if mel_data.size > 0:
                    result_chunk.append(chunk)
            doc.chunks = result_chunk


class AudioCLIPCrafter(Executor):
    TARGET_SAMPLE_RATE = 44000

    @requests
    def craft(self, docs: Optional[DocumentArray], **kwargs):
        if not docs: return
        for doc in docs:
            for chunk in doc.chunks:

                resample = torchaudio.transforms.Resample(
                    orig_freq=chunk.tags['sample_rate'],
                    new_freq=self.TARGET_SAMPLE_RATE
                )

                chunk.blob = resample(torch.Tensor(chunk.blob)).cpu().numpy()
                chunk.tags['sample_rate'] = self.TARGET_SAMPLE_RATE


class TimeSegmenter(Executor):
    def __init__(self, chunk_duration: int = 10, chunk_strip: int = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunk_duration = chunk_duration  # seconds
        self.strip = chunk_strip

    @requests(on=['/search', '/index'])
    def segment(
        self, docs: Optional[DocumentArray] = None, parameters: dict = {}, **kwargs
    ):
        if not docs:
            return
        for idx, doc in enumerate(docs):
            doc.blob, sample_rate = self._load_raw_audio(doc)
            doc.tags['sample_rate'] = sample_rate
            chunk_size = int(self.chunk_duration * sample_rate)
            strip = parameters.get('chunk_strip', self.strip)
            strip_size = int(strip * sample_rate)
            num_chunks = max(1, int((doc.blob.shape[0] - chunk_size) / strip_size))
            for chunk_id in range(num_chunks):
                beg = chunk_id * strip_size
                end = beg + chunk_size
                if beg > doc.blob.shape[0]:
                    break
                doc.chunks.append(
                    Document(
                        blob=doc.blob[beg:end],
                        offset=idx,
                        location=[beg, end],
                        tags=doc.tags,
                    )
                )

    def _load_raw_audio(self, doc: Document) -> Tuple[np.ndarray, int]:
        if doc.blob is not None and doc.tags.get('sample_rate', None) is None:
            raise BadDocType('data is blob but sample rate is not provided')
        elif doc.blob is not None:
            return doc.blob, int(doc.tags['sample_rate'])
        elif doc.uri is not None and doc.uri.endswith('.mp3'):
            return self._read_mp3(doc.uri)
        elif doc.uri is not None and doc.uri.endswith('.wav'):
            return self._read_wav(doc.uri)
        else:
            raise BadDocType('doc needs to have either a blob or a wav/mp3 uri')

    def _read_wav(self, file_path: str) -> Tuple[np.ndarray, int]:
        data, sample_rate = torchaudio.load(file_path)
        data = np.mean(data.cpu().numpy(), axis=0)
        return data, sample_rate

    def _read_mp3(self, file_path: str) -> Tuple[np.ndarray, int]:
        return lr.load(file_path)


class DebugExecutor(Executor):
    @requests
    def debug(self, docs: Optional[DocumentArray] = None, **kwargs):
        logger = get_logger(self)
        if not docs:
            return
        for i, doc in enumerate(docs):
            for match in doc.matches:
                logger.info(f"doc {doc.tags['file']} match: ", match.tags['file'])
