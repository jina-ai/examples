import os
from typing import Dict, List
import numpy as np

from jina.executors.devices import TorchDevice
from jina.executors.rankers import Match2DocRanker
from jina.executors.decorators import batching_multi_input

cur_dir = os.path.dirname(os.path.abspath(__file__))


class FinBertQARanker(TorchDevice, Match2DocRanker):
    """
    :class:`FinBertQARanker` Compute QA relevancy scores using a fine-tuned BERT model.
    """

    batch_size = 16

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

        self.tokenizer = AutoTokenizer.from_pretrained(self.pretrained_model_name_or_path, do_lower_case=True)
        self.model = BertForSequenceClassification.from_pretrained(self.pretrained_model_name_or_path, cache_dir=None,
                                                                   num_labels=2)
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device), strict=False)
        self.to_device(self.model)
        self.model.eval()

    @batching_multi_input(num_data=2)
    def _get_score(self, queries: List[str], answers: List[str]):
        import torch
        from torch.nn.functional import softmax

        # Create inputs for the model
        ids = []
        tokens = []
        masks = []
        for query, answer in zip(queries, answers):
            encoded_seq = self.tokenizer.encode_plus(query, answer,
                                                     max_length=self.max_length,
                                                     pad_to_max_length=True,
                                                     return_token_type_ids=True,
                                                     return_attention_mask=True)

            ids.append(encoded_seq['input_ids'])
            tokens.append(encoded_seq['token_type_ids'])
            masks.append(encoded_seq['attention_mask'])

        # Numericalized, padded, clipped seq with special tokens
        input_ids = torch.tensor(ids).to(self.device)
        # Specify question seq and answer seq
        token_type_ids = torch.tensor(tokens).to(self.device)
        # Specify which position is part of the seq which is padded
        att_mask = torch.tensor(masks).to(self.device)
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
        rel_score = rel_score[:, 1]

        return rel_score

    def score(
            self, query_meta: Dict, old_match_scores: Dict, match_meta: Dict
    ) -> "np.ndarray":

        queries = [query_meta['text'] for _ in range(0, len(old_match_scores))]
        matches = [match_meta[match_id]['text'] for match_id in old_match_scores.keys()]

        scores = self._get_score(queries, matches)

        # Compute new matching scores using a fine-tuned model.
        new_scores = [
            (
                match_id,
                scores[i]
            )
            for i, match_id in enumerate(old_match_scores.keys())
        ]
        return np.array(
            new_scores, dtype=[(self.COL_MATCH_HASH, np.int64), (self.COL_SCORE, np.float64)]
        )
