import io
from typing import Dict, List

import numpy as np
from jina.executors.segmenters import BaseSegmenter
from jina.executors.decorators import single, batching


class PDFSegmenter(BaseSegmenter):
    """
    :class:`PDFExtractorSegmenter` Extracts data (text and images) from PDF files.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @single(slice_nargs=3)
    def segment(self, uri: str, buffer: bytes, mime_type: str, *args, **kwargs) -> List[Dict]:
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
        :param mime_type: the type of data
        :returns: A list of documents with the extracted data
        :rtype: List[Dict]
        """
        chunks = []
        if mime_type != 'application/pdf':
            return chunks
        import fitz  # fitz is a library used in `PyMuPDF` to read pdf and images
        import pdfplumber

        if uri:
            try:
                pdf_img = fitz.open(uri)
                pdf_text = pdfplumber.open(uri)
            except Exception as ex:
                self.logger.error(f'Failed to open {uri}: {ex}')
                return chunks
        elif buffer:
            try:
                pdf_img = fitz.open(stream=buffer, filetype='pdf')
                pdf_text = pdfplumber.open(io.BytesIO(buffer))
            except Exception as ex:
                self.logger.error(f'Failed to load from buffer')
                return chunks
            else:
                self.logger.error('No value found in `buffer` or `uri`')
            return chunks

        # Extract images
        with pdf_img:
            for page in range(len(pdf_img)):
                for img in pdf_img.getPageImageList(page):
                    xref = img[0]
                    pix = fitz.Pixmap(pdf_img, xref)
                    # read data from buffer and reshape the array into 3-d format
                    np_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n).astype('float32')
                    if pix.n - pix.alpha < 4:  # if gray or RGB
                        if pix.n == 1: #convert gray to rgb
                            np_arr_rgb = np.concatenate((np_arr,)*3,-1)
                            chunks.append(dict(blob=np_arr_rgb, weight=1.0, mime_type='image/png'))
                        elif pix.n == 4: # remove transparency layer
                            np_arr_rgb = np_arr[..., :3]
                            chunks.append(dict(blob=np_arr_rgb, weight=1.0, mime_type='image/png'))
                        else:
                            chunks.append(dict(blob=np_arr, weight=1.0, mime_type='image/png'))
                    else:  # if CMYK:
                        pix = fitz.Pixmap(fitz.csRGB, pix)  # Convert to RGB
                        np_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n).astype(
                            'float32')
                        chunks.append(
                            dict(blob=np_arr, weight=1.0, mime_type='image/png'))

        # Extract text
        with pdf_text:
            count = len(pdf_text.pages)
            for i in range(count):
                page = pdf_text.pages[i]
                text_page = page.extract_text(x_tolerance=1, y_tolerance=1)
                if text_page:
                    chunks.append(dict(text=text_page, weight=1.0, mime_type='text/plain'))
        return chunks


class TextSegmenter(BaseSegmenter):
    """
    :class:`TextSegmenter` simply store text into chunks.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @single(slice_nargs=4)
    def segment(self, text: str, uri: str, buffer: bytes, mime_type: str, *args, **kwargs) -> List[Dict]:
        """
        Segements text.

        :param text: the text data
        :param uri: File name of PDF
        :type uri: str
        :param buffer: PDF file in bytes
        :type buffer: bytes
        :param mime_type: the type of data
        :returns: A list of documents with the extracted data
        :rtype: List[Dict]
        """

        chunks = []
        if mime_type == 'text/plain':
            chunks.append(dict(text=text, weight=1.0, mime_type='text/plain'))
        return chunks


class TextSegmenterCustomized(BaseSegmenter):
    """
    :class:`TextSegmenterCustomized` segments text into lines
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @single(slice_nargs=4)
    def segment(self, text: str, uri: str, buffer: bytes, mime_type: str, *args, **kwargs) -> List[Dict]:
        """
        Segements text.

        :param text: the text data
        :param uri: File name of PDF
        :type uri: str
        :param buffer: PDF file in bytes
        :type buffer: bytes
        :param mime_type: the type of data
        :returns: A list of documents with the extracted data
        :rtype: List[Dict]
        """
        chunks = []
        if mime_type == 'text/plain':
            temp = text.split('\n')
            for t in temp:
                chunks.append(dict(text=t, weight=1.0, mime_type='text/plain'))
        return chunks


class ImageSegmenter(BaseSegmenter):
    """
    :class:`ImageSegmenter` reads image and stores into chunks.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @single(slice_nargs=3)
    def segment(self,  uri: str, buffer: bytes, mime_type: str, *args, **kwargs) -> List[Dict]:
        """
        Segements image.

        :param uri: File name of image
        :type uri: str
        :param buffer: image file in bytes
        :type buffer: bytes
        :param mime_type: the type of data
        :returns: A list of documents with the extracted data
        :rtype: List[Dict]
        """
        chunks=[]
        if mime_type.startswith('image'):
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

            chunks = [dict(blob=img, weight=1.0, mime_type='image/png')]
            return chunks
        return chunks


class MultimodalSegmenter(BaseSegmenter):
    """
    :class:`MultimodalSegmenter` Extracts data (text and images) from PDF files.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @single
    def _pdf_segment(self, uri: str, buffer: bytes, *args, **kwargs) -> List[Dict]:
        import fitz

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
            count = len(pdf_text.pages)
            for i in range(count):
                page = pdf_text.pages[i]
                text_page = page.extract_text(x_tolerance=1, y_tolerance=1)
                if text_page:
                    chunks.append(dict(text=text_page, weight=1.0, mime_type='text/plain'))
        return chunks

    @single
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

    @single
    def _text_segment(self, text: str):
        chunks = []
        temp = text.split('\n')
        for t in temp:
            chunks.append(dict(text=t, weight=1.0, mime_type='text/plain'))
        return chunks

    @single
    def segment(self, text: str, uri: str, buffer: bytes, mime_type: str, *args, **kwargs) -> List[Dict]:
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

        if mime_type == 'text/plain':
            return self._text_segment(text)
        elif uri:
            if mime_type == 'application/pdf':
                return self._pdf_segment(uri, buffer)
            elif mime_type == 'image/png':
                return self._image_segment(uri, buffer)
            else:
                raise ValueError('Not supported type for this "uri"')
        else:
            raise ValueError('No value found in "text" or "uri"')
