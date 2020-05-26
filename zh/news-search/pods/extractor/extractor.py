__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


from typing import List, Dict

import numpy as np
from jina.executors.crafters.nlp.split import Sentencizer


class WeightSentencizer(Sentencizer):
    def craft(self, buffer: bytes, doc_id: int, *args, ** kwargs) -> List[Dict]:
        content = eval(buffer.decode())['content'].encode('utf-8')
        results = super().craft(content, doc_id)
        weights = np.linspace(1, 0.1, len(results))
        for result, weight in zip(results, weights):
            result['weight'] = weight

        return results