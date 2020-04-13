
from typing import List, Dict

from jina.executors.crafters.nlp.split import Sentencizer


class WeightSentencizer(Sentencizer):
    def craft(self, raw_bytes: bytes, doc_id: int, *args, ** kwargs) -> List[Dict]:
        results = super().craft(raw_bytes, doc_id)
        if len(results) > 1:
            results[0]['weight'] = 0.5
            avg = 0.5 / (len(results) -1)

            for result in results:
                result['weight'] = avg

        return results