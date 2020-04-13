
from typing import List, Dict

from jina.executors.crafters.nlp.split import Sentencizer
import numpy as np


class WeightSentencizer(Sentencizer):
    def craft(self, raw_bytes: bytes, doc_id: int, *args, ** kwargs) -> List[Dict]:
        results = super().craft(raw_bytes, doc_id)
        weights = np.linspace(1, 0, len(results))
        for result, weight in zip(results, weights):
            result['weight'] = weight

        return results