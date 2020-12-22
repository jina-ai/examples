import os
from typing import Optional
import numpy as np
from jina.executors.decorators import batching, as_ndarray
from jina.executors.encoders.helper import reduce_cls
from jina.helper import cached_property
from jina.hub.encoders.nlp.TransformerTorchEncoder import TransformerTorchEncoder


class RBertEncoder(TransformerTorchEncoder):
    """
    Internally, TransformerTFEncoder wraps the tensorflow-version of transformers from huggingface.
    """

    def __init__(
            self,
            pretrained_model_name_or_path: str = 'hfl/chinese-roberta-wwm-ext',
            pooling_strategy: str = 'auto',
            max_length: Optional[int] = 32,
            truncation_strategy: str = 'longest_first',
            model_save_path: Optional[str] = None,
            vocab_file: str = None,
            *args,
            **kwargs
    ):

        super().__init__(*args, **kwargs)
        self.pretrained_model_name_or_path = pretrained_model_name_or_path
        self.pooling_strategy = pooling_strategy
        self.max_length = max_length
        self.truncation_strategy = truncation_strategy
        self.model_save_path = model_save_path
        self.vocab_file = vocab_file

    def __getstate__(self):
        if self.model_save_path:
            if not os.path.exists(self.model_abspath):
                self.logger.info(f'create folder for saving transformer models: {self.model_abspath}')
                os.mkdir(self.model_abspath)
            self.model.save_pretrained(self.model_abspath)
            self.tokenizer.save_pretrained(self.model_abspath)
        return super().__getstate__()

    def array2tensor(self, array):
        import torch
        tensor = torch.tensor(array)
        return tensor.cuda() if self.on_gpu else tensor

    def tensor2array(self, tensor):
        return tensor.cpu().numpy() if self.on_gpu else tensor.numpy()

    @property
    def model_abspath(self) -> str:
        """Get the file path of the encoder model storage
        """
        return self.get_file_from_workspace(self.model_save_path)

    @cached_property
    def model(self):
        from transformers import BertModel
        model = BertModel.from_pretrained(self.pretrained_model_name_or_path)
        self.to_device(model)
        return model

    @cached_property
    def no_gradients(self):
        import torch
        return torch.no_grad

    @cached_property
    def tensor_func(self):
        import torch
        return torch.tensor

    @cached_property
    def tokenizer(self):
        from transformers import BertTokenizer
        tokenizer = BertTokenizer.from_pretrained(self.pretrained_model_name_or_path)
        return tokenizer

    @batching
    @as_ndarray
    def encode(self, data: 'np.ndarray', *args, **kwargs) -> 'np.ndarray':
        """
        :param data: a 1d array of string type in size `B`
        :return: an ndarray in size `B x D`
        """
        try:
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                if self.tokenizer.pad_token is None:
                    self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
            ids_info = self.tokenizer.batch_encode_plus(data,
                                                        max_length=self.max_length,
                                                        truncation=self.truncation_strategy,
                                                        pad_to_max_length=True)
        except ValueError:
            self.model.resize_token_embeddings(len(self.tokenizer))
            ids_info = self.tokenizer.batch_encode_plus(data,
                                                        max_length=self.max_length,
                                                        pad_to_max_length=True)
        token_ids_batch = self.array2tensor(ids_info['input_ids'])
        mask_ids_batch = self.array2tensor(ids_info['attention_mask'])
        with self.no_gradients():
            outputs = self.model(token_ids_batch,
                                 attention_mask=mask_ids_batch,
                                 output_hidden_states=True)

            hidden_states = outputs[-1]
            output_embeddings = hidden_states[-1]
            _mask_ids_batch = self.tensor2array(mask_ids_batch)
            _seq_output = self.tensor2array(output_embeddings)

            output = reduce_cls(_seq_output, _mask_ids_batch)
        return output

