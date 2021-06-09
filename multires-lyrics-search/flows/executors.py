""" Executors required for the multires example """

import re
import string
from typing import Dict, List, Optional

from jina import Executor, DocumentArray, Document, requests
from jina.logging.predefined import default_logger as logger


class Sentencizer(Executor):
    """
    :class:`Sentencizer` split the text on the doc-level
    into sentences on the chunk-level with a rule-base strategy.
    The text is split by the punctuation characters listed in ``punct_chars``.
    The sentences that are shorter than the ``min_sent_len``
    or longer than the ``max_sent_len`` after stripping will be discarded.
    :param min_sent_len: the minimal number of characters,
        (including white spaces) of the sentence, by default 1.
    :param max_sent_len: the maximal number of characters,
        (including white spaces) of the sentence, by default 512.
    :param punct_chars: the punctuation characters to split on,
        whatever is in the list will be used,
        for example ['!', '.', '?'] will use '!', '.' and '?'
    :param uniform_weight: the definition of it should have
        uniform weight or should be calculated
    :param args:  Additional positional arguments
    :param kwargs: Additional keyword arguments
    """
    def __init__(self,
                 min_sent_len: int = 1,
                 max_sent_len: int = 512,
                 punct_chars: Optional[List[str]] = None,
                 uniform_weight: bool = True,
                 *args, **kwargs):
        """Set constructor."""
        super().__init__(*args, **kwargs)
        self.min_sent_len = min_sent_len
        self.max_sent_len = max_sent_len
        self.punct_chars = punct_chars
        self.uniform_weight = uniform_weight
        self.logger = logger
        if not punct_chars:
            self.punct_chars = ['!', '.', '?', '։', '؟', '۔', '܀', '܁', '܂', '‼', '‽', '⁇', '⁈', '⁉', '⸮', '﹖', '﹗',
                                '！', '．', '？', '｡', '。', '\n']
        if self.min_sent_len > self.max_sent_len:
            self.logger.warning('the min_sent_len (={}) should be smaller or equal to the max_sent_len (={})'.format(
                self.min_sent_len, self.max_sent_len))
        self._slit_pat = re.compile('\s*([^{0}]+)(?<!\s)[{0}]*'.format(''.join(set(self.punct_chars))))

    @requests
    def segment(self, docs: DocumentArray, **kwargs) -> DocumentArray:
        """
        Split the text into sentences.
        :param docs: Documents that contain the text
        :param kwargs: Additional keyword arguments
        :return: a list of chunk dicts with the split sentences
        """
        for doc in docs:
            text = doc.text
            ret = [(m.group(0), m.start(), m.end()) for m in
                   re.finditer(self._slit_pat, text)]
            if not ret:
                ret = [(text, 0, len(text))]
            for ci, (r, s, e) in enumerate(ret):
                f = re.sub('\n+', ' ', r).strip()
                f = f[:self.max_sent_len]
                if len(f) > self.min_sent_len:
                    doc.chunks.append(
                        Document(
                            text=f,
                            offset=ci,
                            weight=1.0 if self.uniform_weight else len(f) / len(text),
                            location=[s, e])
                    )
        return docs
