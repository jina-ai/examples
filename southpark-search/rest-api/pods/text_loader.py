from typing import Dict

from jina.executors.crafters import BaseDocCrafter


class TextExtractor(BaseDocCrafter):
    def craft(self, text: str, *args, **kwargs) -> Dict:
        *_, s = text.split('[SEP]')
        return dict(weight=1., text=s, meta_info=text.encode('utf8'))
