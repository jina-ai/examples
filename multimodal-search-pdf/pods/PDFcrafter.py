from jina import Segmenter, Crafter


class SimpleCrafter(Crafter):
    """Simple crafter for multimodal example."""

    def craft(self, tags):
        """
        Read the data and add tags.

        :param tags: tags of data
        :return: crafted data
        """
        a = 1
        return {
            'text': tags['caption'],
            'uri': f'data/people-img/{tags["image"]}',
        }


class PDFSegmenter(Segmenter):
    """Segmenter for multimodal example."""

    def segment(self, text, uri):
        """
        Segment data into text and uri.

        :param text: text data
        :param uri: uri data of images
        :return: Segmented data.
        """
        b = 1
        return [
            {'text': text, 'mime_type': 'text/plain'},
            {'uri': uri, 'mime_type': 'image/jpeg'},
        ]


import io
from typing import Dict, List

import numpy as np

from jina.executors.segmenters import BaseSegmenter


class ImageSegmenter(BaseSegmenter):
    """
    :class:`PDFExtractorSegmenter` Extracts data (text and images) from PDF files.
    """

    def __init__(self, channel_axis: int = -1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_axis = channel_axis

    def segment(self, uri: str, buffer: bytes, *args, **kwargs) -> List[Dict]:
        """
        Segements PDF files. Extracts data from them.

        Checks if the input is a string of the filename,
        or if it's the file in bytes.
        It will then extract the data from the file, creating a list for images,
        and text.

        :param uri: File name of PDF
        :type uri: str
        :param buffer: PDF file in bytes
        :type buffer: bytes
        :returns: A list of documents with the extracted data
        :rtype: List[Dict]
        """

        from PIL import Image

        if buffer:
            raw_img = Image.open(io.BytesIO(buffer))
        elif uri:
            raw_img = Image.open(uri)
        else:
            raise ValueError('no value found in "buffer" and "uri"')
        raw_img = raw_img.convert('RGB')
        img = np.array(raw_img).astype('float32')
        if self.channel_axis != -1:
            img = np.moveaxis(img, -1, self.channel_axis)
        chunks = []
        chunks.append(dict(blob=img, weight=1.0, mime_type='image/png'))
        return chunks


class PDFExtraSegmenter(BaseSegmenter):
    """
    :class:`PDFExtractorSegmenter` Extracts data (text and images) from PDF files.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def segment(self, uri: str, buffer: bytes, *args, **kwargs) -> List[Dict]:
        """
        Segements PDF files. Extracts data from them.

        Checks if the input is a string of the filename,
        or if it's the file in bytes.
        It will then extract the data from the file, creating a list for images,
        and text.

        :param uri: File name of PDF
        :type uri: str
        :param buffer: PDF file in bytes
        :type buffer: bytes
        :returns: A list of documents with the extracted data
        :rtype: List[Dict]
        """


        import fitz
        import PyPDF2

        if uri:
            pdf_img = fitz.open(uri)
            pdf_text = open(uri, 'rb')
        elif buffer:
            pdf_img = fitz.open(stream=buffer, filetype='pdf')
            pdf_text = io.BytesIO(buffer)
        else:
            raise ValueError('No value found in "buffer" or "uri"')

        chunks = []
        # Extract images
        with pdf_img:
            for page in range(len(pdf_img)):
                for img in pdf_img.getPageImageList(page):
                    xref = img[0]
                    pix = fitz.Pixmap(pdf_img, xref)
                    np_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n).astype('float32')
                    if pix.n - pix.alpha < 4:  # if gray or RGB
                        chunks.append(
                            dict(blob=np_arr, weight=1.0, mime_type='image/png'))
                    else:  # if CMYK:
                        pix = fitz.Pixmap(fitz.csRGB, pix)  # Convert to RGB
                        np_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n).astype(
                            'float32')
                        chunks.append(
                            dict(blob=np_arr, weight=1.0, mime_type='image/png'))

        # Extract text
        with pdf_text:
            text = ''
            pdf_reader = PyPDF2.PdfFileReader(pdf_text)
            count = pdf_reader.numPages
            for page in range(count):
                page = pdf_reader.getPage(page)
                text += page.extractText()
            if text:
                chunks.append(
                    dict(text=text, weight=1.0, mime_type='text/plain'))

        return chunks



class MMExtraSegmenter(BaseSegmenter):
    """
    :class:`PDFExtractorSegmenter` Extracts data (text and images) from PDF files.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _pdf_segment(self, uri: str, buffer: bytes, *args, **kwargs) -> List[Dict]:
        import fitz
        import PyPDF2

        pdf_img = fitz.open(uri)
        pdf_text = open(uri, 'rb')

        chunks = []
        # Extract images
        with pdf_img:
            for page in range(len(pdf_img)):
                for img in pdf_img.getPageImageList(page):
                    xref = img[0]
                    pix = fitz.Pixmap(pdf_img, xref)
                    np_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n).astype('float32')
                    if pix.n - pix.alpha < 4:  # if gray or RGB
                        chunks.append(
                            dict(blob=np_arr, weight=1.0, mime_type='image/png'))
                    else:  # if CMYK:
                        pix = fitz.Pixmap(fitz.csRGB, pix)  # Convert to RGB
                        np_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n).astype(
                            'float32')
                        chunks.append(
                            dict(blob=np_arr, weight=1.0, mime_type='image/png'))

        # Extract text
        with pdf_text:
            text = ""
            pdf_reader = PyPDF2.PdfFileReader(pdf_text)
            count = pdf_reader.numPages
            for page in range(count):
                page = pdf_reader.getPage(page)
                text += page.extractText()
            if text:
                temp = text.split('\n')
                for t in temp:
                    chunks.append(dict(text=t, weight=1.0, mime_type='text/plain'))

        return chunks

    def _image_segment(self, uri: str, buffer: bytes, *args, **kwargs) -> List[Dict]:
        from PIL import Image
        self.channel_axis: int = -1

        if buffer:
            raw_img = Image.open(io.BytesIO(buffer))
        elif uri:
            raw_img = Image.open(uri)
        else:
            raise ValueError('no value found in "buffer" and "uri"')
        raw_img = raw_img.convert('RGB')
        img = np.array(raw_img).astype('float32')
        if self.channel_axis != -1:
            img = np.moveaxis(img, -1, self.channel_axis)
        chunks = []
        chunks.append(dict(blob=img, weight=1.0, mime_type='image/png'))
        return chunks

    def _text_segment(self, text: str):
        chunks = []
        temp = text.split('\n')
        for t in temp:
            chunks.append(dict(text=t, weight=1.0, mime_type='text/plain'))
        return chunks

    def segment(self, text: str, uri: str, buffer: bytes, *args, **kwargs) -> List[Dict]:
        """
        Segements PDF files. Extracts data from them.

        Checks if the input is a string of the filename,
        or if it's the file in bytes.
        It will then extract the data from the file, creating a list for images,
        and text.

        :param uri: File name of PDF
        :type uri: str
        :param buffer: PDF file in bytes
        :type buffer: bytes
        :returns: A list of documents with the extracted data
        :rtype: List[Dict]
        """


        if text:
            return self._text_segment(text)
        elif uri:
            file_type = uri.split('.')[-1]
            if file_type == 'pdf':
                return self._pdf_segment(uri, buffer)
            elif file_type == 'png':
                return self._image_segment(uri, buffer)
        else:
            raise ValueError('No value found in "text" or "uri"')
