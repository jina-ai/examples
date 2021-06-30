__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
import io
from typing import Dict, List, Optional, Union, Tuple, Iterable

import fitz
import numpy as np
import pdfplumber
import torch
import torchvision.models as models
from jina import DocumentArray, Executor, requests, Document
from transformers import AutoModel, AutoTokenizer
from jina.logging import default_logger as logger

from flows import helper as helper
from flows.helper import filter_docs


class PDFCrafter(Executor):
    """
    :class:`PDFSegmenter` Extracts data (text and images) from PDF files.

    Stores images (`mime_type`=image/*) on chunk level ('c') and text segments (`mime_type`=text/plain)
    on chunk level ('c') in the root ('r') Document.
    Text is further split by linebreaks and stored on chunk-chunk level ('cc')
    of the `Documents` with `mime_type` == text/plain.
    """
    @requests
    @filter_docs('application/pdf', traversal_path='r')
    def segment(self, docs: DocumentArray, **kwargs):
        """
        Segements PDF files. Extracts data from them.

        Checks if the input is a string of the filename,
        or if it's the file in bytes.
        It will then extract the data from the file, creating a list for images,
        and text.

        :param docs: Array of Documents.

        """
        for doc in docs:
            pdf_img, pdf_text = self._parse_pdf(doc)

            if pdf_img is not None:
                images = self._extract_image(pdf_img)
                doc.chunks += [Document(blob=img, mime_type='image/*') for img in images]
                self._tag_with_root_doc_id(doc, level='c')
            if pdf_text is not None:
                texts = self._extract_text(pdf_text)
                doc.chunks += [Document(text=t, mime_type='text/plain') for t in texts]
                self._tag_with_root_doc_id(doc, level='c')
        return docs

    def _parse_pdf(self, doc: Document):
        pdf_img = None
        pdf_text = None
        try:
            if doc.uri:
                pdf_img = fitz.open(doc.uri)
                pdf_text = pdfplumber.open(doc.uri)
            if doc.buffer:
                pdf_img = fitz.open(stream=doc.buffer, filetype='pdf')
                pdf_text = pdfplumber.open(io.BytesIO(doc.buffer))
        except Exception as ex:
            logger.error(f'Failed to open due to: {ex}')
        return pdf_img, pdf_text

    @staticmethod
    def _extract_text(pdf_text) -> List[str]:
        # Extract text
        with pdf_text:
            texts = []
            count = len(pdf_text.pages)
            for i in range(count):
                page = pdf_text.pages[i]
                texts.append(page.extract_text(x_tolerance=1, y_tolerance=1))
            return texts

    @staticmethod
    def _extract_image(pdf_img) -> List['np.ndarray']:
        with pdf_img:
            images = []
            for page in range(len(pdf_img)):
                for img in pdf_img.getPageImageList(page):
                    xref = img[0]
                    pix = fitz.Pixmap(pdf_img, xref)
                    # read data from buffer and reshape the array into 3-d format
                    np_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n).astype('float32')
                    if pix.n - pix.alpha < 4:  # if gray or RGB
                        if pix.n == 1:  # convert gray to rgb
                            images.append(np.concatenate((np_arr,) * 3, -1))
                        elif pix.n == 4:  # remove transparency layer
                            images.append(np_arr[..., :3])
                        else:
                            images.append(np_arr)
                    else:  # if CMYK:
                        pix = fitz.Pixmap(fitz.csRGB, pix)  # Convert to RGB
                        np_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n).astype(
                            'float32')
                        images.append(np_arr)
        return images

    @staticmethod
    def _tag_with_root_doc_id(doc: Document, level: str):
        for chunk in DocumentArray([doc]).traverse_flat([level]):
            chunk.tags['root_doc_id'] = doc.id


class TextCrafter(Executor):
    @requests(on='/search')
    @filter_docs('text/plain', traversal_path='r')
    def craft(self, docs: DocumentArray, **kwargs):
        for doc in docs:
            doc.chunks.append(Document(doc, copy=True, tags={'root_doc_id': doc.id}))
        return docs


class ImageCrafter(Executor):
    @requests(on='/search')
    @filter_docs('image', traversal_path='r')
    def craft(self, docs: DocumentArray, **kwargs):
        for doc in docs:
            doc.convert_image_uri_to_blob()
            doc.chunks.append(Document(blob=doc.blob, mime_type='image/*'))
        return docs


class MergeCrafts(Executor):
    @requests(on='/search')
    def join_reduce(self, docs_matrix: List[DocumentArray], parameters, **kwargs):
        final_docs = DocumentArray()
        for doc_arr in docs_matrix:
            if not doc_arr:
                continue
            for doc in doc_arr:
                final_docs.append(doc)
        return final_docs


class TextSegmenter(Executor):
    """ Stores text of `Documents` on chunk level and lines (text split by `\n`) on chunk-chunk level."""
    @requests
    @filter_docs('text/plain', 'c')
    def segment(self, docs: DocumentArray, **kwargs):
        for doc in docs:
            doc.chunks += [
                Document(text=t, mime_type='text/plain', tags={'root_doc_id': doc.tags['root_doc_id']}) for t in doc.text.split('\n')]
        return docs


class ImagePreprocessor(Executor):
    def __init__(self, target_size: Union[Iterable[int], int] = 224, img_mean: Tuple[float] = (0, 0, 0),
                 img_std: Tuple[float] = (1, 1, 1), resize_dim: int = 256, channel_axis: int = -1,
                 target_channel_axis: int = 0, *args, **kwargs):
        """Set Constructor."""
        super().__init__(*args, **kwargs)
        if isinstance(target_size, int):
            self.target_size = target_size
        elif isinstance(target_size, Iterable):
            self.target_size = tuple(target_size)
        else:
            raise ValueError(f'target_size {target_size} should be an integer or tuple/list of 2 integers')
        self.resize_dim = resize_dim
        self.img_mean = np.array(img_mean).reshape((1, 1, 3))
        self.img_std = np.array(img_std).reshape((1, 1, 3))
        self.channel_axis = channel_axis
        self.target_channel_axis = target_channel_axis

    @requests
    @filter_docs('image', traversal_path='c')
    def normalize(self, docs: DocumentArray, **kwargs):
        for doc in docs:
            raw_image = helper.load_image(doc.blob, self.channel_axis)
            _img = self._normalize(raw_image)
            _img = helper.move_channel_axis(_img, -1, self.target_channel_axis)
            doc.blob = _img
        return docs

    def _normalize(self, img):
        img = helper.resize_short(img, target_size=self.resize_dim)
        img, _, _ = helper.crop_image(img, target_size=self.target_size, how='center')
        img = np.array(img).astype('float32') / 255
        img -= self.img_mean
        img /= self.img_std
        return img


class TextEncoder(Executor):
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
        self.embedding_fn_name = embedding_fn_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_tokenizer_model)
        self.model = AutoModel.from_pretrained(
            self.pretrained_model_name_or_path, output_hidden_states=True
        )
        self.model.to(torch.device('cpu'))

    def _compute_embedding(self, hidden_states: 'torch.Tensor', input_tokens: Dict):
        fill_vals = {'cls': 0.0, 'mean': 0.0, 'max': -np.inf, 'min': np.inf}
        fill_val = torch.tensor(
            fill_vals[self.pooling_strategy], device=torch.device('cpu')
        )

        layer = hidden_states[self.layer_index]
        attn_mask = input_tokens['attention_mask'].unsqueeze(-1).expand_as(layer)
        layer = torch.where(attn_mask.bool(), layer, fill_val)

        embeddings = layer.sum(dim=1) / attn_mask.sum(dim=1)
        return embeddings.cpu().numpy()

    @requests
    @filter_docs('text/plain', traversal_path='c')
    def encode(self, docs: 'DocumentArray', **kwargs):
        if docs is None:
            return

        texts = docs.get_attributes('text')

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
                k: v.to(torch.device('cpu')) for k, v in input_tokens.items()
            }

            outputs = getattr(self.model, self.embedding_fn_name)(**input_tokens)
            if isinstance(outputs, torch.Tensor):
                return outputs.cpu().numpy()
            hidden_states = outputs.hidden_states

            embeds = self._compute_embedding(hidden_states, input_tokens)
            for doc, embed in zip(docs, embeds):
                doc.embedding = embed

        return docs


class ImageTorchEncoder(Executor):
    """
    :class:`ImageTorchEncoder` encodes ``Document`` content from a ndarray,
    potentially B x (Channel x Height x Width) into a ndarray of `B x D`.
    Where B` is the batch size and `D` is the Dimension.
    Internally, :class:`ImageTorchEncoder` wraps the models from `
    `torchvision.models`.
    https://pytorch.org/docs/stable/torchvision/models.html
    :param model_name: the name of the model. Supported models include
        ``resnet18``, ``alexnet``, `squeezenet1_0``,  ``vgg16``,
        ``densenet161``, ``inception_v3``, ``googlenet``,
        ``shufflenet_v2_x1_0``, ``mobilenet_v2``, ``resnext50_32x4d``,
        ``wide_resnet50_2``, ``mnasnet1_0``
    :param pool_strategy: the pooling strategy. Options are:
        - `None`: Means that the output of the model will be the 4D tensor
            output of the last convolutional block.
        - `mean`: Means that global average pooling will be applied to the
            output of the last convolutional block, and thus the output of
            the model will be a 2D tensor.
        - `max`: Means that global max pooling will be applied.
    :param channel_axis: The axis of the color channel, default is 1
    :param args:  Additional positional arguments
    :param kwargs: Additional keyword arguments
    """

    def __init__(
        self,
        model_name: str = 'mobilenet_v2',
        pool_strategy: str = 'mean',
        channel_axis: int = 1,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.channel_axis = channel_axis
        # axis 0 is the batch
        self._default_channel_axis = 1
        self.model_name = model_name
        if pool_strategy not in ('mean', 'max'):
            raise NotImplementedError(f'unknown pool_strategy: {self.pool_strategy}')
        self.pool_strategy = pool_strategy
        model = getattr(models, self.model_name)(pretrained=True)
        self.model = model.features.eval()
        self.model.to(torch.device('cpu'))
        if self.pool_strategy is not None:
            self.pool_fn = getattr(np, self.pool_strategy)

    def _get_features(self, content):
        return self.model(content)

    def _get_pooling(self, feature_map: 'np.ndarray') -> 'np.ndarray':
        if feature_map.ndim == 2 or self.pool_strategy is None:
            return feature_map
        return self.pool_fn(feature_map, axis=(2, 3))

    @requests
    @filter_docs('image', traversal_path='r')
    def encode(self, docs: DocumentArray, **kwargs):
        if docs is None:
            return

        images = np.stack(docs.get_attributes('blob'))
        images = self._maybe_move_channel_axis(images)

        _input = torch.from_numpy(images)
        features = self._get_features(_input).detach()
        features = self._get_pooling(features.numpy())

        for doc, embed in zip(docs, features):
            doc.embedding = embed

        return docs

    def _maybe_move_channel_axis(self, images) -> 'np.ndarray':
        if self.channel_axis != self._default_channel_axis:
            images = np.moveaxis(images, self.channel_axis, self._default_channel_axis)
        return images


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
    def index(self, docs: DocumentArray, **kwargs):
        self._docs.extend(docs)

    @requests(on='/search')
    def query(self, docs: DocumentArray, **kwargs):
        for doc in docs:
            for match in doc.matches:
                extracted_doc = self._docs[match.id]
                match.MergeFrom(extracted_doc)


class DocVectorIndexer(Executor):
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
    def index(self, docs: 'DocumentArray', **kwargs):
        self._docs.extend(docs)

    @requests(on='/search')
    def search(self, docs: 'DocumentArray', parameters: Dict, **kwargs):
        if docs is None:
            return
        a = np.stack(docs.get_attributes('embedding'))
        b = np.stack(self._docs.get_attributes('embedding'))
        q_emb = helper.ext_A(helper.norm(a))
        d_emb = helper.ext_B(helper.norm(b))
        dists = helper.cosine(q_emb, d_emb)
        top_k = parameters.get('top_k', 3)
        idx, dist = self._get_sorted_top_k(dists, top_k)
        for _q, _ids, _dists in zip(docs, idx, dist):
            for _id, _dist in zip(_ids, _dists):
                d = Document(self._docs[int(_id)], copy=True)
                d.score.value = 1 - _dist
                _q.matches.append(d)

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


class DynamicNModalityRanker(Executor):
    """ This ranker dynamically discovers the number of modalities in the input and ranks them.
        This is useful when your `Flow` shall support queries with different amounts of modality.
    """
    @requests(on='/search')
    def rank(self, docs_matrix: List[DocumentArray], parameters: Dict, **kwargs):
        result = DocumentArray()
        docs_matrix = [doc_arr for doc_arr in docs_matrix if doc_arr is not None and len(doc_arr) > 0]

        for single_doc_per_modality in zip(*docs_matrix):
            final_matches = {}
            for doc in single_doc_per_modality:
                for m in doc.matches:
                    if m.tags['root_doc_id'] in final_matches:
                        final_matches[m.tags['root_doc_id']].score.value += m.score.value
                    else:
                        final_matches[m.tags['root_doc_id']] = Document(id=m.tags['root_doc_id'], score=m.score)
            da = DocumentArray(list(final_matches.values()))
            da.sort(key=lambda ma: ma.score.value, reverse=True)
            d = Document(matches=da[: int(parameters.get('top_k', 3))])
            result.append(d)
        return result
