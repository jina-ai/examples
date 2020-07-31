__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from typing import Dict

from jina.executors.crafters import BaseCrafter


class Splitter(BaseCrafter):
    def craft(self, text: str, *args, **kwargs) -> Dict:
        word, definitions = text.split('+-=')
        return dict(text=definitions, meta_info=word.encode())
