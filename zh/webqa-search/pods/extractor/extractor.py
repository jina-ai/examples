__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import json

from jina.executors.crafters import BaseSegmenter


class WebQATitleExtractor(BaseSegmenter):
    def craft(self, doc_id, text, *args, **kwargs):
        json_dict = json.loads(text)
        title = json_dict['title']
        return [{
                    'doc_id': doc_id,
                    'offset': 0,
                    'length': len(title),
                    'text': title
                }]

