# Test the segmenter.py implementations

from jina import Document, DocumentArray

from pods.segmenters import PDFSegmenter, ImageSegmenter


def test_image_segmenter() -> None:
    docs = DocumentArray([Document(uri='../toy_data/photo-1.png')])
    segmenter = ImageSegmenter()

    segmenter.segment(docs)

    assert len(docs[0].chunks) == 1


def test_pdf_segmenter_creates_chunks() -> None:
    docs = DocumentArray([Document(uri='../toy_data/blog1.pdf')])
    segmenter = PDFSegmenter()

    segmenter.segment(docs)

    assert len(docs[0].chunks) > 0, 'Expected more than zero chunks to be extracted from the PDF'


def test_pdf_segmenter_creates_mime_types() -> None:
    docs = DocumentArray([Document(uri='../toy_data/blog1.pdf')])
    segmenter = PDFSegmenter()

    segmenter.segment(docs)

    for chunk in docs[0].chunks:
        assert chunk.mime_type in ['image/png', 'text/plain']
