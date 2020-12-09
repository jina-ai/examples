import copy
import json
import numpy as np
import torch
from torch.nn.functional import softmax
from transformers import BertTokenizer, BertForSequenceClassification

from jina.executors.rankers import Match2DocRanker

from .. import FinBertQARanker

def test_finbertqaranker():
    """here is my test code

    https://docs.pytest.org/en/stable/getting-started.html#create-your-first-test
    """
    query_meta = {"text": "Why are big companies like Apple or Google not included in the Dow Jones Industrial "
                          "Average (DJIA) index?"}
    query_meta_json = json.dumps(query_meta, sort_keys=True)
    old_match_scores = {1: 5, 2: 7}
    old_match_scores_json = json.dumps(old_match_scores, sort_keys=True)
    match_meta = {1: {"text": "That is a pretty exclusive club and for the most part they are not interested in "
                              "highly volatile companies like Apple and Google. Sure, IBM is part of the DJIA, "
                              "but that is about as stalwart as you can get these days. The typical profile for a "
                              "DJIA stock would be one that pays fairly predictable dividends, has been around since "
                              "money was invented, and are not going anywhere unless the apocalypse really happens "
                              "this year. In summary, DJIA is the boring reliable company index."},
                  2: {"text": "In  most  cases  you  cannot  do  reverse  lookup  on  tax  id  in  the  US.  You  can "
                              " verify ,  but  for  that  you  need  to  have  more  than  just  the  FEIN/SSN.  You  "
                              "should  also  have  a  name ,  and  some  times  address.  Non-profits ,  specifically "
                              ",  have  to  publish  their  EIN  to  donors ,  so  it  may  be  easier  than  others  "
                              "to  identify  those.  Other  businesses  may  not  be  as  easy  to  find  just  by  "
                              "EIN."}}
    match_meta_json = json.dumps(match_meta, sort_keys=True)

    pretrained_model = 'models/bert-qa'
    model_path = "models/2_finbert-qa-50_512_16_3e6.pt"

    ranker = FinBertQARanker(pretrained_model_name_or_path=pretrained_model, model_path=model_path)

    new_scores = ranker.score(
        copy.deepcopy(query_meta),
        copy.deepcopy(old_match_scores),
        copy.deepcopy(match_meta)
    )

    # new_scores = [(1, 0.7607551217079163), (2, 0.0001482228108216077)]
    np.testing.assert_approx_equal(new_scores[0][1], 0.7607, significant=4)
    np.testing.assert_approx_equal(round(new_scores[1][1], 4), 0.0001, significant=4)

    # Guarantee no side-effects happen
    assert query_meta_json == json.dumps(query_meta, sort_keys=True)
    assert old_match_scores_json == json.dumps(old_match_scores, sort_keys=True)
    assert match_meta_json == json.dumps(match_meta, sort_keys=True)
