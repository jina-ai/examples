__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import json

from jina.executors.crafters import BaseSegmenter

class WebQATitleExtractor(BaseSegmenter):
    def craft(self, doc_id, buffer, *args, **kwargs):
        json_dict = json.loads(buffer.decode('utf-8'))
        title = json_dict['title']
        return [{
                    'buffer': title.encode('utf-8'),
                    'doc_id': doc_id,
                    'offset': 0,
                    'length': len(title),
                    'text': title
                }]

