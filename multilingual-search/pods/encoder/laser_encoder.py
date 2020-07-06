__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import numpy as np
from pathlib import Path
from laserembeddings import Laser

from jina.executors.encoders import BaseTextEncoder
from jina.executors.decorators import batching, as_ndarray


class LaserEncoder(BaseTextEncoder):
    def __init__(self, 
                 path_to_bpe_codes: str = Laser.DEFAULT_BPE_CODES_FILE, 
                 path_to_bpe_vocab: str = Laser.DEFAULT_BPE_VOCAB_FILE, 
                 path_to_encoder: str = Laser.DEFAULT_ENCODER_FILE, 
                 language: str = 'en',
                 *args, 
                 **kwargs):
        """
        
        Encoder for language-agnostic sentence representations (Laser) from Facebook research (https://github.com/facebookresearch/LASER)
        
        :param path_to_bpe_codes: path to bpe codes from Laser. Defaults to Laser.DEFAULT_BPE_CODES_FILE.
        :param path_to_bpe_vocab: path to bpe vocabs from Laser. Defaults to Laser.DEFAULT_BPE_VOCAB_FILE.
        :param path_to_encoder: path to the encoder from Laser. Defaults to Laser.DEFAULT_ENCODER_FILE.
        :param language: language to be passed whie creating the embedding. Defaults to en.
        """
        if not Path(path_to_bpe_codes):
            self.logger.error(f'bpe code file {path_to_bpe_codes} not found')
        else:
            self._path_to_bpe_codes = path_to_bpe_codes
        
        if not Path(path_to_bpe_vocab):
            self.logger.error(f'bpe vocab file {path_to_bpe_vocab} not found')
        else:
            self._path_to_bpe_vocab = path_to_bpe_vocab
        
        if not Path(path_to_encoder):
            self._logger.error(f'encode file {path_to_encoder} not found')
        else:
            self._path_to_encoder = path_to_encoder
        
        self.language = language
        super().__init__(*args, **kwargs)
        
    def post_init(self):
        """
        
        creates Laser object to be used to create the embedding during encode
        """
        try:
            self.laser = Laser(bpe_codes=self._path_to_bpe_codes,
                               bpe_vocab=self._path_to_bpe_vocab,
                               encoder=self._path_to_encoder)
        except Exception as exp:
            self.logger.error(f'Got the following exception while instantiating Laser model {exp}')
        
    @batching
    @as_ndarray
    def encode(self, data: 'np.ndarray', *args, **kwargs) -> 'np.ndarray':
        """
        
        :param data: a 1d array of string type in size `B`
        :return: an ndarray in size `B x D` (D=1024)
        """
        output = self.laser.embed_sentences(sentences = data,
                                            lang = self.language)
        return output
