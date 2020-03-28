
import json

from jina.executors.transformers import BaseSegmenter

class WebQAAnswerExtractor(BaseSegmenter):
    def transform(self, raw_bytes, *args, **kwargs):
        json_dict = json.loads(raw_bytes.decode("utf-8"))
        chunks = []
        for idx, answer in enumerate(json_dict['answers']):
            content = answer['content']
            chunks.append({
                    "raw_bytes": content.encode("utf-8"),
                    "chunk_id": answer['answer_id'],
                    "doc_id": json_dict['qid'],
                    "offset": idx,
                    "length": len(content),
                    "text": content
                })

        return chunks

class WebQATitleExtractor(BaseSegmenter):
    def transform(self, raw_bytes, *args, **kwargs):
        json_dict = json.loads(raw_bytes.decode("utf-8"))
        title = json_dict['title']
        return [{
                    "raw_bytes": title.encode("utf-8"),
                    "chunk_id": json_dict['qid'],
                    "doc_id": json_dict['qid'],
                    "offset": 0,
                    "length": len(title),
                    "text": title
                }]

