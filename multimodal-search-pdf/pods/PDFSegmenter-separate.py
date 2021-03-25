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

    @single(slice_nargs=3, flatten_output=False)
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
        :returns: A list of documents with the extracted data
        :rtype: List[Dict]
        """
        chunks=[]
        if mime_type == 'application/pdf':
            import fitz
            import PyPDF2
            import pdfplumber

            if uri:
                pdf_img = fitz.open(uri)
                #pdf_text = open(uri, 'rb')
                pdf_text = pdfplumber.open(uri)
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
                # text = ''
                #pdf_reader = PyPDF2.PdfFileReader(pdf_text)
                count = len(pdf_text.pages)
                for i in range(count):
                    page = pdf_text.pages[i]
                    text_page = page.extract_text(x_tolerance=1, y_tolerance=1)
                    chunks.append(dict(text=text_page, weight=1.0, mime_type='text/plain'))
                    '''
                    if text_page:
                        text_array = text_page.split('\n')
                        length=len(text_array)
                        chunks.append(dict(text=text_array[length//2], weight=1.0, mime_type='text/plain'))
                    '''
        return chunks


class MultimodalSegmenter(BaseSegmenter):
    """
    :class:`PDFExtractorSegmenter` Extracts data (text and images) from PDF files.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @single
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
                text_page = page.extractText()
                chunks.append(
                    dict(text=text_page, weight=1.0, mime_type='text/plain'))

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


class TextSegmenter(BaseSegmenter):
    """
    :class:`PDFExtractorSegmenter` Extracts data (text and images) from PDF files.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def _text_segment(self, text: str):
        chunks = []
        temp = text.split('\n')
        for t in temp:
            chunks.append(dict(text=t, weight=1.0, mime_type='text/plain'))
        return chunks

    @single(slice_nargs=4, flatten_output=False)
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
            #chunks=[]
            return [dict(text=text, weight=1.0, mime_type='text/plain')]
            #return self._text_segment(text)


class TextSegmenterCustomized(BaseSegmenter):
    """
    :class:`PDFExtractorSegmenter` Extracts data (text and images) from PDF files.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def _text_segment(self, text: str):
        chunks = []
        print(text)
        temp = text.split('\n')
        for t in temp:
            chunks.append(dict(text=t, weight=1.0, mime_type='text/plain'))
        print(chunks)
        return chunks

    @single(slice_nargs=4, flatten_output=False)
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


class ImageSegmenter(BaseSegmenter):
    """
    :class:`PDFExtractorSegmenter` Extracts data (text and images) from PDF files.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @single(slice_nargs=3, flatten_output=False)
    def segment(self,  uri: str, buffer: bytes, mime_type: str, *args, **kwargs) -> List[Dict]:
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
        chunks=[]
        if uri:
            if mime_type == 'image/png':
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
