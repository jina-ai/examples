import os
from typing import Dict
import numpy as np

from jina.executors.devices import TorchDevice
from jina.executors.rankers import Match2DocRanker

cur_dir = os.path.dirname(os.path.abspath(__file__))

class FinBertQARanker(TorchDevice, Match2DocRanker):
    """
    :class:`FinBertQARanker` Compute QA relevancy scores using a fine-tuned BERT model.
    """

    required_keys = {"text"}

    def __init__(
            self,
            pretrained_model_name_or_path: str = os.path.join(cur_dir, "models/bert-qa"),
            model_path: str = os.path.join(cur_dir, "models/2_finbert-qa-50_512_16_3e6.pt"),
            max_length: int = 512,
            *args, **kwargs):
        """
        :param pretrained_model_name_or_path: the name of the pre-trained model.
        :param model_path: the path of the fine-tuned model.
        :param max_length: the max length to truncate the tokenized sequences to.
        """

        super().__init__(*args, **kwargs)
        self.pretrained_model_name_or_path = pretrained_model_name_or_path
        self.model_path = model_path
        self.max_length = max_length

    def post_init(self):
        super().post_init()
        import torch
        from transformers import BertForSequenceClassification, AutoTokenizer

        # Initialize device, tokenizer, and model
        self.device = torch.device("cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(self.pretrained_model_name_or_path, do_lower_case=True)
        self.model = BertForSequenceClassification.from_pretrained(self.pretrained_model_name_or_path, cache_dir=None, num_labels=2)
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device), strict=False)
        self.to_device(self.model)
        self.model.eval()

    def _get_score(self, query, answer):
        """
        :param query: question string
        :param answer: answer string
        """
        import torch
        from torch.nn.functional import softmax

        # Create input embeddings for the model
        encoded_seq = self.tokenizer.encode_plus(query, answer,
                                            max_length=self.max_length,
                                            pad_to_max_length=True,
                                            return_token_type_ids=True,
                                            return_attention_mask=True)
        # Numericalized, padded, clipped seq with special tokens
        input_ids = torch.tensor([encoded_seq['input_ids']]).to(self.device)
        # Specify which position of the embedding is the question or answer
        token_type_ids = torch.tensor([encoded_seq['token_type_ids']]).to(self.device)
        # Specify which position of the embedding is padded
        att_mask = torch.tensor([encoded_seq['attention_mask']]).to(self.device)
        # Don't calculate gradients
        with torch.no_grad():
            # Forward pass, calculate logit predictions for each QA pair
            outputs = self.model(input_ids, token_type_ids=token_type_ids, attention_mask=att_mask)
        # Get the predictions
        logits = outputs[0]
        # Apply activation function to get the relevancy score
        rel_score = softmax(logits, dim=1)
        rel_score = rel_score.numpy()
        # Probability that the QA pair is relevant
        rel_score = rel_score[:, 1][0]

        return rel_score

    def score(
            self, query_meta: Dict, old_match_scores: Dict, match_meta: Dict
    ) -> "np.ndarray":

        # Compute new matching scores using a fine-tuned model.
        new_scores = [
            (
                match_id,
                self._get_score(query_meta['text'], match_meta[match_id]['text']),
             )
            for match_id, old_score in old_match_scores.items()
        ]
        return np.array(
            new_scores
            ,
            dtype=[(self.COL_MATCH_HASH, np.int64), (self.COL_SCORE, np.float64)],
        )