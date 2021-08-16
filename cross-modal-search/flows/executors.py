""" Implementation of filters for images and texts"""

import numpy as np
from jina import Executor, DocumentArray, requests


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


class TextFilter(Executor):
    @requests
    def filter_text(self, docs: 'DocumentArray', **kwargs):
        docs = DocumentArray(list(filter(lambda doc: doc.mime_type == 'text/plain', docs)))
        return docs
