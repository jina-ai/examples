import os
from typing import Dict, Iterable, Union, Tuple, Sequence

import torch
import numpy as np
import clip
import json
from PIL import Image
import io
from jina import Executor, DocumentArray, requests, Document
from jina.types.score import NamedScore


def _get_ones(x, y):
    return np.ones((x, y))


def _norm(A):
    return A / np.linalg.norm(A, ord=2, axis=1, keepdims=True)


def _ext_B(B):
    nB, dim = B.shape
    B_ext = _get_ones(dim * 3, nB)
    B_ext[:dim] = (B ** 2).T
    B_ext[dim : 2 * dim] = -2.0 * B.T
    del B
    return B_ext


def _ext_A(A):
    nA, dim = A.shape
    A_ext = _get_ones(nA, dim * 3)
    A_ext[:, dim : 2 * dim] = A
    A_ext[:, 2 * dim :] = A ** 2
    return A_ext


def _cosine(A_norm_ext, B_norm_ext):
    return A_norm_ext.dot(B_norm_ext).clip(min=0) / 2


class ReciprocalRankEvaluator(Executor):

    @staticmethod
    def _evaluate(actual: Sequence[Union[str, int]], desired: Sequence[Union[str, int]], *args, **kwargs) -> float:
        """
        Evaluate score as per reciprocal rank metric.

        :param actual: Sequence of sorted document IDs.
        :param desired: Sequence of sorted relevant document IDs
            (the first is the most relevant) and the one to be considered.
        :param args:  Additional positional arguments
        :param kwargs: Additional keyword arguments
        :return: Reciprocal rank score
        """
        if len(actual) == 0 or len(desired) == 0:
            return 0.0
        try:
            return 1.0 / (actual.index(desired[0]) + 1)
        except:
            return 0.0

    @requests(on='/search')
    def rank_evaluate(self, docs: 'DocumentArray', groundtruths, **kwargs):
        for doc, gt in zip(docs, groundtruths):
            actual_ids = doc.matches.get_attributes('tags__id')
            desired_ids = gt.matches.get_attributes('tags__id')
            mrr = self._evaluate(actual_ids, desired_ids)
            doc.evaluations['mrr'] = mrr


class ImageReader(Executor):
    @requests(on='/index')
    def index_read(self, docs: 'DocumentArray', **kwargs):
        array = DocumentArray(list(filter(lambda doc: doc.modality=='image', docs)))
        for doc in array:
            doc.convert_image_buffer_to_blob()
            doc.blob = np.array(doc.blob).astype(np.uint8)
        return array

    @requests(on='/search')
    def search_read(self, docs: 'DocumentArray', **kwargs):
        image_docs = DocumentArray(list(filter(lambda doc: doc.mime_type in ('image/jpeg', 'image/png'), docs)))
        if not image_docs:
            return DocumentArray([])
        for doc in image_docs:
            doc.convert_uri_to_buffer()
            doc.convert_image_buffer_to_blob()
            doc.blob = doc.blob.astype(np.uint8)
        return image_docs


class ImageNormalizer(Executor):
    def __init__(self,
                 target_size: Union[Iterable[int], int] = 224,
                 img_mean: Tuple[float] = (0, 0, 0),
                 img_std: Tuple[float] = (1, 1, 1),
                 resize_dim: int = 256,
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

    @requests(on=['/index', '/search'])
    def craft(self, docs: 'DocumentArray', *args, **kwargs) -> Dict:
        """
        Normalize the image.
        :param blob: the ndarray of the image with the color channel at the last axis
        :return: a chunk dict with the normalized image
        """
        if not docs:
            return
        for doc in docs:
            img = Image.open(io.BytesIO(doc.buffer))
            img = self._normalize(img)
            doc.content = np.array(img).astype('float32')
            doc.blob = np.moveaxis(doc.blob, -1, 0)
            # doc.content = img

    def _normalize(self, img):
        img = self._resize_short(img, target_size=self.resize_dim)
        img, _, _ = self._crop_image(img, target_size=self.target_size, how='center')
        img = np.array(img).astype('float32') / 255
        img -= self.img_mean
        img /= self.img_std
        return img

    @staticmethod
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

    @staticmethod
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
    def __init__(self, filename='data.ndjson', **kwargs):
        super().__init__(**kwargs)

        self.filename = filename
        self._docs = DocumentArray()
        self.doc_embeddings = np.array([])
        if os.path.exists(self.save_path):
            with open(self.save_path) as fp:
                for v in fp:
                    d = Document(v)
                    self._docs.append(d)
            embeddings = self._docs.get_attributes('embedding')
            if len(embeddings) > 0:
                self._embedding_matrix = _ext_B(_norm(np.stack(embeddings)))

    @property
    def save_path(self):
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)
        return os.path.join(self.workspace, self.filename)

    def close(self) -> None:
        with open(self.save_path, 'w') as fp:
            for d in self._docs:
                json.dump(d.dict(), fp)
                fp.write('\n')

    @requests(on='/index')
    def index(self, docs: 'DocumentArray', **kwargs):
        self._docs.extend(docs)

    @requests(on='/search')
    def search(self, docs: 'DocumentArray', parameters: Dict = {'top_k': 5}, **kwargs):
        if not docs:
            return
        embedding_list = docs.get_attributes('embedding')
        if not embedding_list:
            return
        if not hasattr(self, '_embedding_matrix'):
            return
        doc_embeddings = np.stack(embedding_list)
        q_emb = _ext_A(_norm(doc_embeddings))
        dists = _cosine(q_emb, self._embedding_matrix)
        positions, dist = self._get_sorted_top_k(dists, int(parameters.get('top_k', 5)))
        for _q, _positions, _dists in zip(docs, positions, dist):
            l = []
            for position, _dist in zip(_positions, _dists):
                d = Document(self._docs[int(position)])
                d.scores['cosine'] = 1 - _dist
                _q.matches.append(d)
                l.append(d.id)

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
    def index(self, docs: DocumentArray, **kwargs):
        for doc in docs:
            doc.convert_buffer_to_uri()
        self._docs.extend(docs)

    @requests(on='/search')
    def query(self, docs: DocumentArray, **kwargs):
        if not docs:
            return
        for doc in docs:
            for match in doc.matches:
                if match.id in self._docs:
                    score = match.scores['cosine']
                    match.MergeFrom(self._docs[match.id])
                    match.scores['cosine'] = score


class CLIPImageEncoder(Executor):
    """Encode image into embeddings."""

    def __init__(self, model_name: str = 'ViT-B/32', *args, **kwargs):
        super().__init__(*args, **kwargs)
        torch.set_num_threads(1)
        self.model, _ = clip.load(model_name, 'cpu')

    @requests
    def encode(self, docs: DocumentArray, **kwargs):
        if not docs:
            return
        with torch.no_grad():
            for doc in docs:
                content = np.expand_dims(doc.content, axis=0)
                input = torch.from_numpy(content.astype('float32'))
                embed = self.model.encode_image(input)
                doc.embedding = embed.cpu().numpy().flatten()


class CLIPTextEncoder(Executor):
    """Encode text into embeddings."""

    def __init__(self, model_name: str = 'ViT-B/32', *args, **kwargs):
        super().__init__(*args, **kwargs)
        torch.set_num_threads(1)
        self.model, _ = clip.load(model_name, 'cpu')

    @requests
    def encode(self, docs: DocumentArray, **kwargs):
        _docs = DocumentArray(list(filter(lambda doc: doc.mime_type in ('text/plain',), docs)))
        if not _docs:
            print(f'not text doc is found: {[d.modality for d in docs]}')
            return
        with torch.no_grad():
            for doc in _docs:
                input_torch_tensor = clip.tokenize(doc.content)
                embed = self.model.encode_text(input_torch_tensor)
                doc.embedding = embed.cpu().numpy().flatten()
        return _docs
