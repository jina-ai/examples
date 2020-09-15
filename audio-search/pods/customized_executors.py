import numpy as np
from typing import Any, List, Dict

from jina.executors.encoders import BaseEncoder
from jina.executors.decorators import batching
from jina.executors.crafters import BaseSegmenter


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

