import json, re
from zhon.hanzi import punctuation
from jina.executors.crafters import BaseCrafter


class SubtitleExtractor(BaseCrafter):

    def craft(self, text, *args, **kwargs):
        json_dict = json.loads(text)
        content = json_dict['content'].strip()

        return dict(text=content, offset=0, weight=1.0)
