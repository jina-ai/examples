""" Executors required for the multires example """

import re
from typing import Dict, List, Optional, Union, Tuple, Iterable
import numpy as np
import torch
import os
from transformers import AutoModel, AutoTokenizer

from jina import Executor, DocumentArray, Document, requests
from jina.logging.predefined import default_logger as logger
from helper import _ext_A, _ext_B, _norm, _euclidean


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


class TransformerTorchEncoder(Executor):
    """Transformer executor class """
    def __init__(
        self,
        pretrained_model_name_or_path: str = 'sentence-transformers/distilbert-base-nli-stsb-mean-tokens',
        base_tokenizer_model: Optional[str] = None,
        pooling_strategy: str = 'mean',
        layer_index: int = -1,
        max_length: Optional[int] = None,
        acceleration: Optional[str] = None,
        embedding_fn_name: str = '__call__',
        device: str = 'cpu',
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.pretrained_model_name_or_path = pretrained_model_name_or_path
        self.base_tokenizer_model = (
            base_tokenizer_model or pretrained_model_name_or_path
        )
        self.pooling_strategy = pooling_strategy
        self.layer_index = layer_index
        self.max_length = max_length
        self.acceleration = acceleration
        if not device in ['cpu', 'cuda']:
            logger.error('Torch device not supported. Must be cpu or cuda!')
            raise RuntimeError('Torch device not supported. Must be cpu or cuda!')
        self.device = device
        self.embedding_fn_name = embedding_fn_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_tokenizer_model)
        self.model = AutoModel.from_pretrained(
            self.pretrained_model_name_or_path, output_hidden_states=True
        )
        self.model.to(torch.device(device))

    def _compute_embedding(self, hidden_states: 'torch.Tensor', input_tokens: Dict):
        fill_vals = {'cls': 0.0, 'mean': 0.0, 'max': -np.inf, 'min': np.inf}
        fill_val = torch.tensor(
            fill_vals[self.pooling_strategy], device=torch.device(self.device)
        )
        layer = hidden_states[self.layer_index]
        attn_mask = input_tokens['attention_mask'].unsqueeze(-1).expand_as(layer)
        layer = torch.where(attn_mask.bool(), layer, fill_val)
        embeddings = layer.sum(dim=1) / attn_mask.sum(dim=1)
        return embeddings.cpu().numpy()

    @requests
    def encode(self, docs: 'DocumentArray', **kwargs):
        chunks = docs.traverse_flat(['c'])
        texts = chunks.get_attributes('text')

        with torch.no_grad():
            if not self.tokenizer.pad_token:
                self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
                self.model.resize_token_embeddings(len(self.tokenizer.vocab))
            input_tokens = self.tokenizer(
                texts,
                max_length=self.max_length,
                padding='longest',
                truncation=True,
                return_tensors='pt',
            )
            input_tokens = {
                k: v.to(torch.device(self.device)) for k, v in input_tokens.items()
            }
            outputs = getattr(self.model, self.embedding_fn_name)(**input_tokens)
            if isinstance(outputs, torch.Tensor):
                return outputs.cpu().numpy()
            hidden_states = outputs.hidden_states
            embeds = self._compute_embedding(hidden_states, input_tokens)
            for doc, embed in zip(chunks, embeds):
                doc.embedding = embed
        return docs


class EmbeddingIndexer(Executor):
    def __init__(self, index_file_name: str, **kwargs):
        super().__init__(**kwargs)
        self.index_file_name = index_file_name
        if os.path.exists(self.save_path):
            self._docs = DocumentArray.load(self.save_path)
        else:
            self._docs = DocumentArray()

    @property
    def save_path(self):
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
        return os.path.join(self.workspace, self.index_file_name)

    def close(self):
        self._docs.save(self.save_path)

    @requests(on='/index')
    def index(self, docs: 'DocumentArray', **kwargs) -> DocumentArray:
        chunks = docs.traverse_flat(['c'])
        embedding_docs = DocumentArray()
        for doc in chunks:
            embedding_docs.append(Document(id=doc.id, embedding=doc.embedding))
        self._docs.extend(embedding_docs)
        return docs

    @requests(on='/search')
    def search(self, docs: 'DocumentArray', parameters: Dict, **kwargs) \
            -> DocumentArray:
        chunks = docs.traverse_flat(['c'])
        a = np.stack(chunks.get_attributes('embedding'))
        b = np.stack(self._docs.get_attributes('embedding'))
        q_emb = _ext_A(_norm(a))
        d_emb = _ext_B(_norm(b))
        dists = _euclidean(q_emb, d_emb)
        top_k = int(parameters.get('top_k', 5))
        assert top_k > 0
        idx, dist = self._get_sorted_top_k(dists, top_k)
        for _q, _ids, _dists in zip(chunks, idx, dist):
            for _id, _dist in zip(_ids, _dists):
                doc = Document(self._docs[int(_id)], copy=True)
                doc.score.value = 1 - _dist
                doc.parent_id = int(_id)
                _q.matches.append(doc)
        return docs

    @staticmethod
    def _get_sorted_top_k(
        dist: 'np.array', top_k: int
    ) -> Tuple['np.ndarray', 'np.ndarray']:
        if top_k >= dist.shape[1]:
            idx = dist.argsort(axis=1)[:, :top_k]
            dist = np.take_along_axis(dist, idx, axis=1)
        else:
            idx_ps = dist.argpartition(kth=top_k, axis=1)[:, :top_k]
            dist = np.take_along_axis(dist, idx_ps, axis=1)
            idx_fs = dist.argsort(axis=1)
            idx = np.take_along_axis(idx_ps, idx_fs, axis=1)
            dist = np.take_along_axis(dist, idx_fs, axis=1)

        return idx, dist


class KeyValueIndexer(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.path.exists(self.save_path):
            self._docs = DocumentArray.load(self.save_path)
        else:
            self._docs = DocumentArray()

    @property
    def save_path(self):
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
        return os.path.join(self.workspace, 'kv.json')

    def close(self):
        self._docs.save(self.save_path)

    @requests(on='/index')
    def index(self, docs: DocumentArray, **kwargs) -> DocumentArray:
        self._docs.extend(docs)
        return docs

    @requests(on='/search')
    def query(self, docs: DocumentArray, **kwargs) -> DocumentArray:
        chunks = self._docs.traverse_flat(['c'])
        for match in docs.traverse_flat(['cm']):
            extracted_doc = None
            for doc in self._docs:
                if chunks[int(match.parent_id)].parent_id == doc.id:
                    print(chunks[int(match.parent_id)].text)
                    extracted_doc = doc
                    break

            extracted_doc.tags['chunk_id'] = match.parent_id
            extracted_doc.tags['chunk_text'] = match.text
            match.MergeFrom(extracted_doc)
        return docs