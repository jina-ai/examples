import os

import numpy as np
import torch
from jina.executors.decorators import batching, as_ndarray
from jina.executors.encoders import BaseTextEncoder
from jina.executors.encoders.helper import reduce_mean, reduce_max, reduce_min


class TransformerRobertaEncoder(BaseTextEncoder):
    def __init__(self,
                 pooling_strategy: str = 'cls',
                 max_length: int = 128,
                 model_path: str = 'transformer',
                 *args, **kwargs):
        """

        :param pooling_strategy: the strategy to merge the word embeddings into the chunk embedding. Supported
            strategies include 'cls', 'mean', 'max', 'min'.
        :param max_length: the max length to truncate the tokenized sequences to.
        :param model_path: the path of the encoder model. If a valid path is given, the encoder will be loaded from the
            given path.
        """
        super().__init__(*args, **kwargs)
        self.model = None
        self.tokenizer = None
        self.pooling_strategy = pooling_strategy
        self.max_length = max_length
        self.raw_model_path = model_path

    def post_init(self):
        from transformers import BertTokenizer, BertModel

        if os.path.exists(self.model_abspath):
            self._tmp_model_path = self.model_abspath
        else:
            self._tmp_model_path = 'hfl/chinese-roberta-wwm-ext'

        self.tokenizer = BertTokenizer.from_pretrained(self._tmp_model_path)
        self.tokenizer.padding_side = 'right'

        self.model = BertModel.from_pretrained(self._tmp_model_path)

    @batching
    @as_ndarray
    def encode(self, data: 'np.ndarray', *args, **kwargs) -> 'np.ndarray':
        """

        :param data: a 1d array of string type in size `B`
        :return: an ndarray in size `B x D`
        """
        token_ids_batch = []
        mask_ids_batch = []
        for c_idx in range(data.shape[0]):
            token_ids = self.tokenizer.encode(
                data[c_idx], pad_to_max_length=True, max_length=self.max_length)
            mask_ids = [0 if t == self.tokenizer.pad_token_id else 1 for t in token_ids]
            token_ids_batch.append(token_ids)
            mask_ids_batch.append(mask_ids)

        token_ids_batch = torch.tensor(token_ids_batch)
        mask_ids_batch = torch.tensor(mask_ids_batch)

        with torch.no_grad():
            seq_output, pooler_output, *_ = self.model(token_ids_batch, attention_mask=mask_ids_batch)
            if self.pooling_strategy == 'cls':
                output = pooler_output.cpu().numpy()

            elif self.pooling_strategy == 'mean':
                output = reduce_mean(seq_output.numpy(), mask_ids_batch.numpy())
            elif self.pooling_strategy == 'max':
                output = reduce_max(seq_output.numpy(), mask_ids_batch.numpy())
            elif self.pooling_strategy == 'min':
                output = reduce_min(seq_output.numpy(), mask_ids_batch.numpy())
            else:
                self.logger.error("pooling strategy not found: {}".format(self.pooling_strategy))
                raise NotImplementedError

        return output

    @property
    def model_abspath(self) -> str:
        """Get the file path of the encoder model storage

        """
        return self.get_file_from_workspace(self.raw_model_path)