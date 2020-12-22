import re
import string
from typing import Dict, List

from jina.executors.crafters import BaseSegmenter


class Sent2Chunk(BaseSegmenter):
    """
    :class:`Sentencizer` split the text on the doc-level into sentences on the chunk-level with a rule-base strategy.
        The text is split by the punctuation characters listed in ``punct_chars``.
        The sentences that are shorter than the ``min_sent_len`` or longer than the ``max_sent_len`` after stripping will be discarded.
    """

    def __init__(self,
                 min_sent_len: int = 1,
                 max_sent_len: int = 512,
                 punct_chars: str = None,
                 uniform_weight: bool = True,
                 *args, **kwargs):
        """

        :param min_sent_len: the minimal number of characters (including white spaces) of the sentence, by default 1.
        :param max_sent_len: the maximal number of characters (including white spaces) of the sentence, by default 1e5.
        :param punct_chars: the punctuation characters to split on.
        """
        super().__init__(*args, **kwargs)
        self.min_sent_len = min_sent_len
        self.max_sent_len = max_sent_len
        self.punct_chars = punct_chars
        self.uniform_weight = uniform_weight
        if not punct_chars:
            self.punct_chars = ['，', '。']
        if self.min_sent_len > self.max_sent_len:
            self.logger.warning('the min_sent_len (={}) should be smaller or equal to the max_sent_len (={})'.format(
                self.min_sent_len, self.max_sent_len))
        self._slit_pat = re.compile('\s*([^{0}]+)(?<!\s)[{0}]*'.format(''.join(set(self.punct_chars))))

    def craft(self, text: str, *args, **kwargs) -> List[Dict]:
        """
        Split the text into sentences.

        :param text: the raw text
        :return: a list of chunk dicts with the cropped images
        """

        results = []
        ret = [(m.group(0), m.start(), m.end()) for m in
               re.finditer(self._slit_pat, text)]
        if not ret:
            ret = [(text, 0, len(text))]
        for ci, (r, s, e) in enumerate(ret):
            f = r.replace("，", "").replace("。", "")
            f = f[:self.max_sent_len]
            if len(f) > self.min_sent_len:
                results.append(dict(
                    text=f,
                    offset=ci,
                    weight=1.0 if self.uniform_weight else len(f) / len(text),
                    location=[s, e]
                ))
            print("f:=======", f)
        return results
