from jina.executors.crafters import BaseDocCrafter
import json


class DictEntryExtractor(BaseDocCrafter):
    def craft(self, doc_id, raw_bytes, *args, **kwargs):
        json_str = raw_bytes.decode('utf8')
        json_dict = json.loads(json_str)
        word = json_dict['word']
        def_text = json_dict['text']
        weight = json_dict['weight']
        doc_dict = {
            'raw_bytes': f'{word}: {def_text}'.encode('utf8'),
            'doc_id': doc_id,
            'weight': weight,
            'meta_info': raw_bytes
        }
        return doc_dict

