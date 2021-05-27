import os
from typing import Dict, Optional, List, Iterable, Union, Tuple

import numpy as np

from jina import Executor, DocumentArray, requests, Document

Class CompoundIndexer(Executor):


def __init__(
        self,
        pretrained_model_name_or_path: str = 'sentence-transformers/distilbert-base-nli-stsb-mean-tokens',
        base_tokenizer_model: Optional[str] = None,
        pooling_strategy: str = 'mean',
        layer_index: int = -1,
        max_length: Optional[int] = None,
        acceleration: Optional[str] = None,
        embedding_fn_name: str = '__call__',
        *args,
        **kwargs,
):
    super().__init__(*args, **kwargs)