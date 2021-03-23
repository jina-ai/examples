import os

from jina import Segmenter, Crafter


class SimpleCrafter(Crafter):
    """Simple crafter for multimodal example."""

    def craft(self, tags):
        """
        Read the data and add tags.

        :param tags: tags of data
        :return: crafted data
        """
        print("")
        return {
            'text': tags['caption'],
            'uri': f'data/people-img/{tags["image"]}',
        }


class BiSegmenter(Segmenter):
    """Segmenter for multimodal example."""

    def segment(self, text, uri):
        """
        Segment data into text and uri.

        :param text: text data
        :param uri: uri data of images
        :return: Segmented data.
        """
        return [
            {'text': text, 'mime_type': 'text/plain'},
            {'uri': uri, 'mime_type': 'image/jpeg'},
        ]
