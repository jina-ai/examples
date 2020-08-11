__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import json

from jina.executors.crafters import BaseSegmenter


class WebQATitleExtractor(BaseSegmenter):
    def craft(self, text, *args, **kwargs):
        json_dict = json.loads(text)
        title = json_dict['title']
        return [{
                    'offset': 0,
                    'length': len(title),
                    'text': title
                }]
