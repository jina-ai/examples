
import json

from jina.executors.crafters import BaseSegmenter

class WebQAAnswerExtractor(BaseSegmenter):
    def craft(self, doc_id, raw_bytes, *args, **kwargs):
        json_dict = json.loads(raw_bytes.decode('utf-8'))
        chunks = []
        for idx, answer in enumerate(json_dict['answers']):
            content = answer['content']
            chunks.append({
                    'raw_bytes': content.encode('utf-8'),
                    'doc_id': doc_id,
                    'offset': idx,
                    'length': len(content),
                    'text': content
                })

        return chunks

class WebQATitleExtractor(BaseSegmenter):
    def craft(self, doc_id, raw_bytes, *args, **kwargs):
        json_dict = json.loads(raw_bytes.decode('utf-8'))
        title = json_dict['title']
        return [{
                    'raw_bytes': title.encode('utf-8'),
                    'doc_id': doc_id,
                    'offset': 0,
                    'length': len(title),
                    'text': title
                }]

