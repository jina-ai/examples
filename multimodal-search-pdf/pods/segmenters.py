import io

import fitz
import pdfplumber
import numpy as np
from PIL import Image

from jina import Executor, requests, DocumentArray, Document
from jina.logging import JinaLogger


class LoggerMixing:
    def __init__(self):
        self.logger = JinaLogger(self.__class__.__name__)


class PDFSegmenter(Executor, LoggerMixing):
    """
    :class:`PDFSegmenter` Extracts data (text and images) from PDF files.
    """

    @requests(on=['index', 'search'])
    def segment(self, docs: DocumentArray, **kwargs):
        """
        Segements PDF files. Extracts data from them.

        Checks if the input is a string of the filename,
        or if it's the file in bytes.
        It will then extract the data from the file, creating a list for images,
        and text.

        :param docs: Array of Documents.

        """
        docs = PDFSegmenter._filter_pdf(docs)
        for doc in docs:
            pdf_img, pdf_text = self._parse_pdf(doc)

            # Extract images
            if pdf_img is not None:
                self._extract_image(doc, pdf_img)

            if pdf_text is not None:
                self._extract_text(doc, pdf_text)

    @staticmethod
    def _filter_pdf(docs: DocumentArray) -> DocumentArray:
        return DocumentArray([doc for doc in docs if doc.mime_type == 'application/pdf'])

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
            self.logger.error(f'Failed to open due to: {ex}')
        return pdf_img, pdf_text

    @staticmethod
    def _extract_text(doc, pdf_text):
        # Extract text
        with pdf_text:
            count = len(pdf_text.pages)
            for i in range(count):
                page = pdf_text.pages[i]
                text_page = page.extract_text(x_tolerance=1, y_tolerance=1)
                if text_page:
                    doc.chunks.append(Document(text=text_page, weight=1.0, mime_type='text/plain'))

    @staticmethod
    def _extract_image(doc, pdf_img):
        with pdf_img:
            for page in range(len(pdf_img)):
                for img in pdf_img.getPageImageList(page):
                    xref = img[0]
                    pix = fitz.Pixmap(pdf_img, xref)
                    # read data from buffer and reshape the array into 3-d format
                    np_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n).astype('float32')
                    if pix.n - pix.alpha < 4:  # if gray or RGB
                        if pix.n == 1:  # convert gray to rgb
                            np_arr_rgb = np.concatenate((np_arr,) * 3, -1)
                            doc.chunks.append(Document(blob=np_arr_rgb, weight=1.0, mime_type='image/png'))
                        elif pix.n == 4:  # remove transparency layer
                            np_arr_rgb = np_arr[..., :3]
                            doc.chunks.append(Document(blob=np_arr_rgb, weight=1.0, mime_type='image/png'))
                        else:
                            doc.chunks.append(Document(blob=np_arr, weight=1.0, mime_type='image/png'))
                    else:  # if CMYK:
                        pix = fitz.Pixmap(fitz.csRGB, pix)  # Convert to RGB
                        np_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n).astype(
                            'float32')
                        doc.chunks.append(
                            Document(blob=np_arr, weight=1.0, mime_type='image/png'))


class TextIntoLinesSegmenter(Executor, LoggerMixing):
    """
    :class:`TextSegmenterCustomized` segments text into lines
    """
    @requests(on=['index', 'search'])
    def segment(self, docs: DocumentArray, **kwargs):
        for doc in docs:
            if doc.mime_type == 'text/plain':
                doc.chunks += [Document(text=t, weight=1.0, mime_type='text/plain') for t in doc.text.split('\n')]


class ImageSegmenter(Executor, LoggerMixing):
    """
    :class:`ImageSegmenter` reads image and stores into chunks.
    """
    @requests(on=['index', 'search'])
    def segment(self, docs: DocumentArray, **kwargs):
        for doc in docs:
            if doc.mime_type.startswith('image'):
                if doc.buffer:
                    raw_img = Image.open(io.BytesIO(doc.buffer))
                elif doc.uri:
                    raw_img = Image.open(doc.uri)
                else:
                    raise ValueError('no value found in "buffer" and "uri"')
                raw_img = raw_img.convert('RGB')
                img = np.array(raw_img).astype('float32')
                doc.chunks.append(Document(blob=img, weight=1.0, mime_type='image/png'))
