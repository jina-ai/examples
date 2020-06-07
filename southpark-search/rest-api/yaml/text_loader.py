import os
import urllib.request
import urllib.parse
from typing import Dict

from jina.executors.crafters import BaseDocCrafter


class TextReader(BaseDocCrafter):
    def craft(self, buffer: bytes, uri: str, text: str, *args, **kwargs) -> Dict:
        if text:
            _text = text
        elif uri:
            _buffer = b''
            if urllib.parse.urlparse(uri).scheme in {'http', 'https', 'data'}:
                page = urllib.request.Request(uri, headers={'User-Agent': 'Mozilla/5.0'})
                tmp = urllib.request.urlopen(page)
                _buffer = tmp.read()
            elif os.path.exists(uri):
                with open(uri, 'rb') as fp:
                    _buffer = fp.read()
            else:
                raise FileNotFoundError(f'{uri} is not a URL or a valid local path')
            _text = _buffer.decode('utf8')
        elif buffer:
            _text = buffer.decode('utf8')
        else:
            raise ValueError('no value found in "buffer", "uri" and "text"')
        return dict(weight=1., text=_text)

