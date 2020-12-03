from typing import Dict
import numpy as np
import torch
from torch.nn.functional import softmax
from transformers import BertTokenizer, BertForSequenceClassification
from jina.executors.rankers import Match2DocRanker

device = torch.device("cpu")

class QAReranker(Match2DocRanker):
    """
    :class:`QAReranker` Compute QA relevancy scores using a fine-tuned BERT model.
    """

    required_keys = {"text"}

    def get_score(self, query, answer):
        # Load the BERT tokenizer.
        print('\nLoading BERT tokenizer...')
        tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
        model = BertForSequenceClassification.from_pretrained('bert-base-uncased', cache_dir=None, num_labels=2)
        model.load_state_dict(torch.load('model/2_finbert-qa-50_512_16_3e6.pt', map_location=torch.device('cpu')), strict=False)
        model.to(device)
        model.eval()

        # Create inputs for the model
        encoded_seq = tokenizer.encode_plus(query, answer,
                                            max_length=512,
                                            pad_to_max_length=True,
                                            return_token_type_ids=True,
                                            return_attention_mask=True)
        # Numericalized, padded, clipped seq with special tokens
        input_ids = torch.tensor([encoded_seq['input_ids']]).to(device)
        # Specify question seq and answer seq
        token_type_ids = torch.tensor([encoded_seq['token_type_ids']]).to(device)
        # Specify which position is part of the seq which is padded
        att_mask = torch.tensor([encoded_seq['attention_mask']]).to(device)
        # Don't calculate gradients
        with torch.no_grad():
            # Forward pass, calculate logit predictions for each QA pair
            outputs = model(input_ids, token_type_ids=token_type_ids, attention_mask=att_mask)
        # Get the predictions
        logits = outputs[0]
        # Apply activation function
        rel_score = softmax(logits, dim=1)
        # Move logits and labels to CPU
        rel_score = rel_score.detach().cpu().numpy()
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
            new_scores,
            dtype=[(self.COL_MATCH_HASH, np.int64), (self.COL_SCORE, np.float64)],
        )