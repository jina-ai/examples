import os
from typing import Dict, Optional, List, Iterable, Union, Tuple

import itertools
import torch
import numpy as np
import clip

# import transformers
# from transformers import DistilBertModel, DistilBertConfig

from jina import Executor, DocumentArray, requests, Document

class ImageReader(Executor):
    def __init__(self, channel_axis=0, **kwargs):
        super().__init__(**kwargs)
        self.docs = DocumentArray()
        self.channel_axis = channel_axis

    # with:
    #     channel_axis: 0

    @requests(on='/index')
    def index_read(self, docs: 'DocumentArray', **kwargs):
        image_docs = DocumentArray(list(itertools.filterfalse(lambda doc: doc.modality != 'image', docs)))
        self.docs.extend(image_docs)
        #IndexRequest:
        #      - !FilterQL
        #        with:
        #          lookups: {'modality': 'image'}
        #      - !CraftDriver {}

    @requests(on='/search')
    def search_read(self, docs: 'DocumentArray', **kwargs):
        image_docs = DocumentArray(list(itertools.filterfalse(lambda doc: 'image' not in doc.mime_type, docs)))
        for doc in image_docs:
            doc.convert_uri_to_buffer()
            doc.pop('chunks', 'uri')
        #    SearchRequest:
        #      - !FilterQL
        #        with:
        #          lookups: {'mime_type__contains': 'image'}
        #      - !URI2Buffer {}
        #      - !ExcludeQL
        #        with:
        #          fields:
        #            - chunks
        #            - uri
        #      - !CraftDriver {}

class ImageNormalizer(Executor):
    def __init__(self,
                 target_size: Union[Iterable[int], int] = 224,
                 img_mean: Tuple[float] = (0, 0, 0),
                 img_std: Tuple[float] = (1, 1, 1),
                 resize_dim: int = 256,
                 channel_axis: int = -1,
                 target_channel_axis: int = -1,
                 *args,
                 **kwargs):
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

    @requests(on=['/index', '/search'])
    def craft(self, docs: 'DocumentArray', *args, **kwargs) -> Dict:
        """
        Normalize the image.
        :param blob: the ndarray of the image with the color channel at the last axis
        :return: a chunk dict with the normalized image
        """
        for doc in docs:
            '''
            for chunk in doc.chunks:
            #if chunk.mime_type == 'image/png':
                raw_img = _load_image(chunk.blob, self.channel_axis)
                _img = self._normalize(raw_img)
                # move the channel_axis to target_channel_axis to better fit different models
                img = _move_channel_axis(_img, -1, self.target_channel_axis)
                chunk.blob = img'''
            doc.convert_uri_to_datauri(base64=True)
            doc.tags['datauri'] = doc.uri
            doc.convert_image_datauri_to_blob()
            raw_img = _load_image(doc.content, self.channel_axis)
            _img = self._normalize(raw_img)
            # move the channel_axis to target_channel_axis to better fit different models
            img = _move_channel_axis(_img, -1, self.target_channel_axis)
            doc.content = img

    def _normalize(self, img):
        img = _resize_short(img, target_size=self.resize_dim)
        img, _, _ = _crop_image(img, target_size=self.target_size, how='center')
        img = np.array(img).astype('float32') / 255
        img -= self.img_mean
        img /= self.img_std
        return img

def _move_channel_axis(
    img: 'np.ndarray', channel_axis_to_move: int, target_channel_axis: int = -1
) -> 'np.ndarray':
    """
    Ensure the color channel axis is the default axis.
    """
    if channel_axis_to_move == target_channel_axis:
        return img
    return np.moveaxis(img, channel_axis_to_move, target_channel_axis)


def _load_image(blob: 'np.ndarray', channel_axis: int):
    """
    Load an image array and return a `PIL.Image` object.
    """

    from PIL import Image

    img = _move_channel_axis(blob, channel_axis)
    return Image.fromarray(img.astype('uint8'))


def _crop_image(
    img,
    target_size: Union[Tuple[int, int], int],
    top: int = None,
    left: int = None,
    how: str = 'precise',
):
    """
    Crop the input :py:mod:`PIL` image.
    :param img: :py:mod:`PIL.Image`, the image to be resized
    :param target_size: desired output size. If size is a sequence like
        (h, w), the output size will be matched to this. If size is an int,
        the output will have the same height and width as the `target_size`.
    :param top: the vertical coordinate of the top left corner of the crop box.
    :param left: the horizontal coordinate of the top left corner of the crop box.
    :param how: the way of cropping. Valid values include `center`, `random`, and, `precise`. Default is `precise`.
        - `center`: crop the center part of the image
        - `random`: crop a random part of the image
        - `precise`: crop the part of the image specified by the crop box with the given ``top`` and ``left``.
        .. warning:: When `precise` is used, ``top`` and ``left`` must be fed valid value.
    """
    import PIL.Image as Image

    assert isinstance(img, Image.Image), 'img must be a PIL.Image'
    img_w, img_h = img.size
    if isinstance(target_size, int):
        target_h = target_w = target_size
    elif isinstance(target_size, Tuple) and len(target_size) == 2:
        target_h, target_w = target_size
    else:
        raise ValueError(
            f'target_size should be an integer or a tuple of two integers: {target_size}'
        )
    w_beg = left
    h_beg = top
    if how == 'center':
        w_beg = int((img_w - target_w) / 2)
        h_beg = int((img_h - target_h) / 2)
    elif how == 'random':
        w_beg = np.random.randint(0, img_w - target_w + 1)
        h_beg = np.random.randint(0, img_h - target_h + 1)
    elif how == 'precise':
        assert w_beg is not None and h_beg is not None
        assert (
            0 <= w_beg <= (img_w - target_w)
        ), f'left must be within [0, {img_w - target_w}]: {w_beg}'
        assert (
            0 <= h_beg <= (img_h - target_h)
        ), f'top must be within [0, {img_h - target_h}]: {h_beg}'
    else:
        raise ValueError(f'unknown input how: {how}')
    if not isinstance(w_beg, int):
        raise ValueError(f'left must be int number between 0 and {img_w}: {left}')
    if not isinstance(h_beg, int):
        raise ValueError(f'top must be int number between 0 and {img_h}: {top}')
    w_end = w_beg + target_w
    h_end = h_beg + target_h
    img = img.crop((w_beg, h_beg, w_end, h_end))
    return img, h_beg, w_beg


def _resize_short(img, target_size, how: str = 'LANCZOS'):
    """
    Resize the input :py:mod:`PIL` image.
    :param img: :py:mod:`PIL.Image`, the image to be resized
    :param target_size: desired output size. If size is a sequence like (h, w), the output size will be matched to
        this. If size is an int, the smaller edge of the image will be matched to this number maintain the aspect
        ratio.
    :param how: the interpolation method. Valid values include `NEAREST`, `BILINEAR`, `BICUBIC`, and `LANCZOS`.
        Default is `LANCZOS`. Please refer to `PIL.Image` for detaisl.
    """
    import PIL.Image as Image

    assert isinstance(img, Image.Image), 'img must be a PIL.Image'
    if isinstance(target_size, int):
        percent = float(target_size) / min(img.size[0], img.size[1])
        target_w = int(round(img.size[0] * percent))
        target_h = int(round(img.size[1] * percent))
    elif isinstance(target_size, Tuple) and len(target_size) == 2:
        target_h, target_w = target_size
    else:
        raise ValueError(
            f'target_size should be an integer or a tuple of two integers: {target_size}'
        )
    img = img.resize((target_w, target_h), getattr(Image, how))
    return img

class NumpyIndexer(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._docs = DocumentArray()

    @requests(on='/index')
    def index(self, docs: 'DocumentArray', **kwargs):
        self._docs.extend(docs)


    @requests(on='/search')
    def search(self, docs: 'DocumentArray', parameters: Dict = None, **kwargs):
        if parameters is None:
            parameters = {'top_k': 5}

        doc_embeddings = np.stack(docs.get_attributes('embedding'))
        q_emb = _ext_A(_norm(doc_embeddings))
        d_emb = _ext_B(_norm(self._docs.get_attributes('embedding')))
        dists = _cosine(q_emb, d_emb)
        positions, dist = self._get_sorted_top_k(dists, int(parameters['top_k']))
        for _q, _positions, _dists in zip(docs, positions, dist):
            for position, _dist in zip(_positions, _dists):
                d = Document(self._docs[int(position)])
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

def _get_ones(x, y):
    return np.ones((x, y))

def _ext_A(A):
    nA, dim = A.shape
    A_ext = _get_ones(nA, dim * 3)
    A_ext[:, dim : 2 * dim] = A
    A_ext[:, 2 * dim :] = A ** 2
    return A_ext

def _ext_B(B):
    nB, dim = B.shape
    B_ext = _get_ones(dim * 3, nB)
    B_ext[:dim] = (B ** 2).T
    B_ext[dim : 2 * dim] = -2.0 * B.T
    del B
    return B_ext

def _euclidean(A_ext, B_ext):
    sqdist = A_ext.dot(B_ext).clip(min=0)
    return np.sqrt(sqdist)

def _norm(A):
    return A / np.linalg.norm(A, ord=2, axis=1, keepdims=True)

def _cosine(A_norm_ext, B_norm_ext):
    return A_norm_ext.dot(B_norm_ext).clip(min=0) / 2


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
                extracted_doc = self._docs[match.parent_id]
                match.MergeFrom(extracted_doc)


class CLIPImageEncoder(Executor):
    """Encode image into embeddings."""

    def __init__(self, model_name: str = 'ViT-B/32', *args, **kwargs):
        super().__init__(*args, **kwargs)
        torch.set_num_threads(1)
        model, _ = clip.load(model_name, 'cpu')
        self.model = model

    @requests
    def encode(self, docs: DocumentArray, **kwargs):
        with torch.no_grad():
            for doc in docs:
                #content = np.expand_dims(doc.content, axis=0)
                input = torch.from_numpy(doc.content().astype('float32'))
                embed = self.model.encode_image(input)
                doc.embedding = embed.cpu().numpy().flatten()


class CLIPTextEncoder(Executor):
    """Encode text into embeddings."""

    def __init__(self, model_name: str = 'ViT-B/32', *args, **kwargs):
        super().__init__(*args, **kwargs)
        torch.set_num_threads(1)
        model, _ = clip.load(model_name, 'cpu')
        self.model = model

    @requests
    def encode(self, docs: DocumentArray, **kwargs):
        docs = DocumentArray(list(itertools.filterfalse(lambda doc: doc.modality != 'text', docs)))
        docs = DocumentArray(list(itertools.filterfalse(lambda doc: 'text' not in doc.mime_type, docs)))
        with torch.no_grad():
            for doc in docs:
                input_torch_tensor = clip.tokenize(doc.content)
                # content = np.expand_dims(doc.content, axis=0)
                # input = torch.from_numpy(content) #.to(torch.int64)
                embed = self.model.encode_text(input_torch_tensor)
                doc.embedding = embed.cpu().numpy().flatten()


# class TextIndexer(Executor):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

# class MergeMatchesSortTopK(Executor):
#     def __init__(self, docs, **kwargs):
#         super().__init__(**kwargs)
#         self.docs = docs
#
#     @requests(on=['/index', '/search', '/train', ''])
#     def merge_and_sort(self, docs, **kwargs):
#         for m in docs.traverse('m'):
#             docs.extend(m)
#         docs = docs[:10]
#         docs.sort(key=score__value)
#         return self.docs

# class RootMerger(Executor):
#     def __init__(self, doc_matrix, **kwargs):
#         super().__init__(**kwargs)
#         self.doc_matrix = doc_matrix
#
#     def merge(self, **kwargs):
#         return self.doc_matrix

