from jina.executors.crafters import BaseSegmenter
from jina.executors.encoders import BaseTextEncoder
import json
import numpy as np


class DictEntryExtractor(BaseSegmenter):
    def craft(self, doc_id, raw_bytes, *args, **kwargs):
        json_str = raw_bytes.decode("utf8")
        json_dict = json.loads(json_str)
        word = json_dict["word"]
        chunk_list = []
        for idx, d in enumerate(json_dict["def"]):
            chunk_text = d["text"]
            chunk_weight = d["weight"]
            chunk_list.append(
                {
                    "raw_bytes": chunk_text.encode("utf8"),
                    "doc_id": doc_id,
                    "offset": idx,
                    "weight": chunk_weight,
                    "length": len(chunk_text),
                    "text": chunk_text
                }
            )
        return chunk_list


class RandomEncoder(BaseTextEncoder):
    def encode(self, data, *args, **kwargs):
        num_chunks = data.shape[0]
        emb_dim = 128
        emb_result = np.random.rand(num_chunks, emb_dim)
        self.logger.info("encode random embedding for the sentences")
        return emb_result
