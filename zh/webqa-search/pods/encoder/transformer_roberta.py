__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

from jina.executors.encoders.nlp.transformer import TransformerTorchEncoder


class TransformerRobertaEncoder(TransformerTorchEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.model_name = 'hfl/chinese-roberta-wwm-ext'
        self.tmp_model_path = 'hfl/chinese-roberta-wwm-ext'
        self.pooling_strategy = 'cls'
        self.max_length = 32

    def get_tokenizer(self):
        from transformers import BertTokenizer
        _tokenizer = BertTokenizer.from_pretrained(self.tmp_model_path)
        _tokenizer.padding_side = 'right'
        return _tokenizer

    def get_model(self):
        from transformers import BertModel
        _model = BertModel.from_pretrained(self.tmp_model_path)
        self.to_device(_model)
        return _model
