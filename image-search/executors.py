__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os
from typing import Tuple, Dict, Union, Iterable, Optional
import numpy as np

from jina import Document, DocumentArray, Executor, requests
from helper import _load_image, _move_channel_axis, _crop_image, _resize_short
from jina.excepts import PretrainedModelFileDoesNotExist
from jina.logging import default_logger as logger


class ImageCrafter(Executor):
    def __init__(
        self,
        target_size: Union[Iterable[int], int] = 224,
        img_mean: Tuple[float] = (0, 0, 0),
        img_std: Tuple[float] = (1, 1, 1),
        resize_dim: int = 256,
        channel_axis: int = -1,
        target_channel_axis: int = -1,
        *args,
        **kwargs,
    ):
        """Set Constructor."""
        super().__init__(*args, **kwargs)
        self.target_size = target_size
        self.resize_dim = resize_dim
        self.img_mean = np.array(img_mean).reshape((1, 1, 3))
        self.img_std = np.array(img_std).reshape((1, 1, 3))
        self.channel_axis = channel_axis
        self.target_channel_axis = target_channel_axis

    def craft(self, docs: DocumentArray, fn) -> DocumentArray:
        filtered_docs = DocumentArray(
            list(
                filter(lambda d: 'image/' in d.mime_type, docs)
            )
        )
        for doc in filtered_docs:
            getattr(doc, fn)()
            raw_img = _load_image(doc.blob, self.channel_axis)
            _img = self._normalize(raw_img)
            # move the channel_axis to target_channel_axis to better fit
            # different models
            img = _move_channel_axis(_img, -1, self.target_channel_axis)
            doc.blob = img
        return filtered_docs

    @requests(on='/index')
    def craft_index(self, docs: DocumentArray, **kwargs) -> DocumentArray:
        return self.craft(docs, 'convert_image_uri_to_blob')

    @requests(on='/search')
    def craft_search(self, docs: DocumentArray, **kwargs) -> DocumentArray:
        return self.craft(docs, 'convert_image_datauri_to_blob')

    def _normalize(self, img):
        img = _resize_short(img, target_size=self.resize_dim)
        img, _, _ = _crop_image(img, target_size=self.target_size, how='center')
        img = np.array(img).astype('float32') / 255
        img -= self.img_mean
        img /= self.img_std
        return img


class BigTransferEncoder(Executor):
    """
    :class:`BigTransferEncoder` is Big Transfer (BiT) presented by
    Google (https://github.com/google-research/big_transfer).
    Uses pretrained BiT to encode data from a ndarray, potentially
    B x (Channel x Height x Width) into a ndarray of `B x D`.
    Internally, :class:`BigTransferEncoder` wraps the models from
    https://storage.googleapis.com/bit_models/.

    .. warning::

        Known issue: this does not work on tensorflow==2.2.0,
        https://github.com/tensorflow/tensorflow/issues/38571

    :param model_path: the path of the model in the `SavedModel` format.
        The pretrained model can be downloaded at
        wget https://storage.googleapis.com/bit_models/Imagenet21k/[model_name]/feature_vectors/saved_model.pb
        wget https://storage.googleapis.com/bit_models/Imagenet21k/[model_name]/feature_vectors/variables/variables.data-00000-of-00001
        wget https://storage.googleapis.com/bit_models/Imagenet21k/[model_name]/feature_vectors/variables/variables.index

        ``[model_name]`` includes `R50x1`, `R101x1`, `R50x3`, `R101x3`, `R152x4`

        The `model_path` should be a directory path, which has the following structure.

        .. highlight:: bash
         .. code-block:: bash

            .
            ├── saved_model.pb
            └── variables
                ├── variables.data-00000-of-00001
                └── variables.index

        :param channel_axis: the axis id of the channel, -1 indicate the color
            channel info at the last axis. If given other, then `
            `np.moveaxis(data, channel_axis, -1)`` is performed before :meth:`encode`.
    """
    def __init__(self,
                 model_path: Optional[str] = 'pretrained',
                 channel_axis: int = 1,
                 on_gpu: bool = False,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_axis = channel_axis
        self.model_path = model_path
        self.on_gpu = on_gpu
        self.logger = logger

        if self.model_path and os.path.exists(self.model_path):
            import tensorflow as tf
            cpus = tf.config.experimental.list_physical_devices(
                device_type='CPU')
            gpus = tf.config.experimental.list_physical_devices(
                device_type='GPU')
            if self.on_gpu and len(gpus) > 0:
                cpus.append(gpus[0])
            tf.config.experimental.set_visible_devices(devices=cpus)
            self.logger.info(f'BiT model path: {self.model_path}')
            from tensorflow.python.keras.models import load_model
            _model = load_model(self.model_path)
            self.model = _model.signatures['serving_default']
            self._get_input = tf.convert_to_tensor
        else:
            raise PretrainedModelFileDoesNotExist(
                f'model at {self.model_path} does not exist')

    @requests
    def encode(self, docs: DocumentArray, **kwargs) -> DocumentArray:
        """
        Encode data into a ndarray of `B x D`.
        Where `B` is the batch size and `D` is the Dimension.

        :param docs: an array in size `B`
        :return: an ndarray in size `B x D`.
        """
        data = np.zeros((docs.__len__(),) + docs[0].blob.shape)
        for index, doc in enumerate(docs):
            data[index] = doc.blob
        if self.channel_axis != -1:
            data = np.moveaxis(data, self.channel_axis, -1)
        _output = self.model(self._get_input(data.astype(np.float32)))
        output = _output['output_1'].numpy()
        for index, doc in enumerate(docs):
            doc.embedding = output[index]
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
        embedding_docs = DocumentArray()
        for doc in docs:
            embedding_docs.append(Document(id=doc.id, embedding=doc.embedding))
        self._docs.extend(embedding_docs)
        return docs

    @requests(on='/search')
    def search(self, docs: 'DocumentArray', parameters: Dict, **kwargs) \
            -> DocumentArray:
        a = np.stack(docs.get_attributes('embedding'))
        b = np.stack(self._docs.get_attributes('embedding'))
        q_emb = _ext_A(_norm(a))
        d_emb = _ext_B(_norm(b))
        dists = _cosine(q_emb, d_emb)
        top_k = int(parameters.get('top_k', 5))
        assert top_k > 0
        idx, dist = self._get_sorted_top_k(dists, top_k)
        for _q, _ids, _dists in zip(docs, idx, dist):
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
        for doc in docs:
            for match in doc.matches:
                extracted_doc = self._docs[int(match.parent_id)]
                # The id fields should be the same
                assert match.id == extracted_doc.id
                match.MergeFrom(extracted_doc)
        return docs


class MatchImageReader(Executor):

    @requests(on='/search')
    def query(self, docs: DocumentArray, **kwargs) -> DocumentArray:
        for doc in docs:
            for match in doc.matches:
                match.convert_image_uri_to_blob()
                match.convert_image_blob_to_uri(96, 96)
        return docs


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
