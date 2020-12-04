from typing import Dict
import numpy as np
import torch
from torch.nn.functional import softmax
from transformers import BertTokenizer, BertForSequenceClassification
from jina.executors.rankers import Match2DocRanker

class QAReranker(Match2DocRanker):
    """
    :class:`QAReranker` Compute QA relevancy scores using a fine-tuned BERT model.
    """

    required_keys = {"text"}

    def __init__(
            self,
            pretrained_model_name_or_path: str,
            model_path: str,
            max_length: int = 512,
            *args, **kwargs):
        """
        :param pretrained_model_name_or_path: Either:
            - a string with the `shortcut name` of a pre-trained model to load from cache or download, e.g.: ``bert-base-uncased``.
            - a string with the `identifier name` of a pre-trained model that was user-uploaded to Hugging Face S3, e.g.: ``dbmdz/bert-base-german-cased``.
            - a path to a `directory` containing model weights saved using :func:`~transformers.PreTrainedModel.save_pretrained`, e.g.: ``./my_model_directory/``.
            - a path or url to a `tensorflow index checkpoint file` (e.g. `./tf_model/model.ckpt.index`). In this case, ``from_tf`` should be set to True and a configuration object should be provided as ``config`` argument.
            This loading path is slower than converting the TensorFlow
            checkpoint in a PyTorch model using the provided conversion scripts and loading the PyTorch model afterwards.
        :param model_name: the path where the model is stored
        :param max_length: the max length to truncate the tokenized sequences to.
        """

        super().__init__(*args, **kwargs)
        self.pretrained_model_name_or_path = pretrained_model_name_or_path
        self.model_path = model_path
        self.max_length = max_length

    def post_init(self):
        super().post_init()
        self.device = torch.device("cpu")
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
        self.model = BertForSequenceClassification.from_pretrained(self.pretrained_model_name_or_path, cache_dir=None, num_labels=2)
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device), strict=False)
        self.model.to(self.device)
        self.model.eval()

    def get_score(self, query, answer):

        # Create inputs for the model
        encoded_seq = self.tokenizer.encode_plus(query, answer,
                                            max_length=self.max_length,
                                            pad_to_max_length=True,
                                            return_token_type_ids=True,
                                            return_attention_mask=True)
        # Numericalized, padded, clipped seq with special tokens
        input_ids = torch.tensor([encoded_seq['input_ids']]).to(self.device)
        # Specify question seq and answer seq
        token_type_ids = torch.tensor([encoded_seq['token_type_ids']]).to(self.device)
        # Specify which position is part of the seq which is padded
        att_mask = torch.tensor([encoded_seq['attention_mask']]).to(self.device)
        # Don't calculate gradients
        with torch.no_grad():
            # Forward pass, calculate logit predictions for each QA pair
            outputs = self.model(input_ids, token_type_ids=token_type_ids, attention_mask=att_mask)
        # Get the predictions
        logits = outputs[0]
        # Apply activation function
        rel_score = softmax(logits, dim=1)
        rel_score = rel_score.numpy()
        # Probability that the QA pair is relevant
        rel_score = rel_score[:, 1][0]

        return rel_score

    def score(
            self, query_meta: Dict, old_match_scores: Dict, match_meta: Dict
    ) -> "np.ndarray":

        new_scores = [
            (
                match_id,
                self.get_score(query_meta['text'], match_meta[match_id]['text']),
             )
            for match_id, old_score in old_match_scores.items()
        ]
        return np.array(
            new_scores
            ,
            dtype=[(self.COL_MATCH_HASH, np.int64), (self.COL_SCORE, np.float64)],
        )