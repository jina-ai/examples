import pytest

import json
import numpy as np

from .. import FinBertQARanker


@pytest.mark.parametrize('batch_size', [1, 2, 3, 100])
def test_finbertqaranker(batch_size):
    query_meta = {"text": "Why are big companies like Apple or Google not included in the Dow Jones Industrial "
                          "Average (DJIA) index?"}
    query_meta_json = json.dumps(query_meta, sort_keys=True)
    old_match_scores = {1: 5, 2: 7, 3: 5}
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
                              "EIN."},
                  3: {"text": "Why are big companies like Apple or Google not included in the Dow Jones Industrial "
                              "Average (DJIA) index?"}
                  }
    match_meta_json = json.dumps(match_meta, sort_keys=True)

    pretrained_model = 'models/bert-qa'
    model_path = "models/2_finbert-qa-50_512_16_3e6.pt"

    ranker = FinBertQARanker(pretrained_model_name_or_path=pretrained_model, model_path=model_path)
    ranker.batch_size = batch_size

    new_scores = ranker.score(
        query_meta,
        old_match_scores,
        match_meta
    )

    # new_scores = [(1, 0.7607551217079163), (2, 0.0001482228108216077), (3, 1.0)]
    np.testing.assert_approx_equal(new_scores[0][1], 0.7607, significant=4)
    np.testing.assert_approx_equal(round(new_scores[1][1], 4), 0.0001, significant=4)
    np.testing.assert_approx_equal(round(new_scores[2][1]), 1.0, significant=4)

    # Guarantee no side-effects happen
    assert query_meta_json == json.dumps(query_meta, sort_keys=True)
    assert old_match_scores_json == json.dumps(old_match_scores, sort_keys=True)
    assert match_meta_json == json.dumps(match_meta, sort_keys=True)


@pytest.mark.parametrize('batch_size', [1, 3, 4, 7, 1000])
def test_finbertqaranker_second(batch_size):
    query_meta = {"text": 'What does it mean that stocks are “memoryless”?'}
    query_meta_json = json.dumps(query_meta, sort_keys=True)
    old_match_scores = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1}
    old_match_scores_json = json.dumps(old_match_scores, sort_keys=True)
    match_meta = {1: {"text": 'It reminds me of the Efficient Market Hypothesis, except that just states in its '
                              'weakest form that the current market price accounts for all information embedded in '
                              'previous market prices. In other words, people buying today at 42 know it was selling '
                              'for 40 yesterday, and the patterns and such. To say that stock is memoryless strikes '
                              'me as not quite right -- to the extent that stocks are valued based on earnings, '
                              'much of what we infer about future earnings relies on past and present earnings. One '
                              'obvious counterexample to this "memoryless" claim is bankruptcy. If a stock files '
                              'bankruptcy, and there isn\'t enough money to pay senior debt, your shares are worth 0 '
                              'in perpetuity.'},
                  2: {"text": 'I think that "memoryless" in this context of a given stock\'s performance is not a '
                              'term of art. IMO, it\'s an anecdotal concept or cliche used to make a point about '
                              'holding a stock. Sometimes people get stuck... they buy a stock or fund at 50, '
                              'it goes down to 30, then hold onto it so they can "get back to even". By holding the '
                              'loser stock for emotional reasons, the person potentially misses out on gains '
                              'elsewhere.'
                      },
                  3: {"text": 'This is an interesting question that may actually be better suited to Quant.SE. First '
                              'of all, stock prices are random variables, or, to be more precise, stochastic '
                              'processes (a time-ordered string of random variables).  The alternative to being '
                              'stochastic is being deterministic, and I doubt you believe that stock prices are '
                              'deterministic (meaning, they are fully knowable in advance).  The fact that real world '
                              'events drive the randomness has no bearing on whether or not it is random.  So, '
                              'to start, I think you have confused the technical definition of random with a '
                              'colloquial concept. Now, the heart of the question is whether stock prices are '
                              'memoryless.  Ultimately, this is an empirical question that has been addressed in many '
                              'academic studies.  The conclusion of most of this research is that stock prices are '
                              '"almost" memoryless, in the sense that the distribution of future stock prices '
                              'displays very little dependence upon past realizations, although a few persistent '
                              'anomalies remain.  One of the most robust deviations from memorylessness is the '
                              'increase in the volatility of a stock following large declines.  Another is '
                              'persistence in volatility.  In general, in fact, the volatility is far more '
                              'predictable than the mean of stock price changes.  Hence "memorylessness" is a far '
                              'stronger assumption than the efficient markets hypothesis. The bottom line, however, '
                              'is that the deviations from memorylessness are relatively small.  As such, despite its '
                              'limitations, it is a decent working assumption in some contexts.'},
                  4: {"text": 'With my current, limited knowledge (see end), I understand it the following way: Are '
                              'share prices really described as "memoryless"?  Yes.  Is there a   technical meaning '
                              'of the term? What does it really mean? The meaning comes from Markov Models: Think of '
                              'the behavior of the stock market over time as a Markov Chain, i.e. a probabilistic '
                              'model with states and probabilistic transitions. A state is the current price of all '
                              'stocks of the market, a transition is a step in time. Memoryless means that '
                              'transitions that the stock market might make can be modelled by a relation from one '
                              'state to another, i.e. it only depends on the current state. The model is a Markov '
                              'Chain, as opposed to a more general Stochastic Process where the next state depends on '
                              'more than the current state. So in a Markov Chain, all the history of one stock is '
                              '"encoded" already in its current price (more precisely in all stock\'s prices).  The '
                              'memorylessness of stocks is the main statement of the Efficient Market Theory (EMT). '
                              'If a company\'s circumstances don\'t change, then a drop in its share price is going '
                              'to be followed by a rise later.  So if the EMT holds, your statement above is not '
                              'necessarily true. I personally belief the EMT is a good approximation - only large '
                              'corporations (e.g. Renaissance Technologies) have enough ressources (hundreds of '
                              'mathematicians, billions of $) to be able to leverage tiny non-random movements that '
                              'stem from a not completely random, mostly chaotic market.  The prices can of course '
                              'change when the company\'s circumstances change, but they aren\'t "memoryless" either. '
                              'A company\'s future state is influenced by its past. In the EMT, a stock\'s future '
                              'state is only influenced by its past as much as is encoded in its current price (more '
                              'precisely, the complete market\'s current state). Whether that price was reached by a '
                              'drop or a rise makes no difference.  The above is my believe, but I\'m by far no '
                              'finance expert. I am working professionally with probabilistic models, but have only '
                              'read one book on finance: Kommer\'s "Souverän investieren mit Indexfonds und ETFs". '
                              'It\'s supposed to contain many statements of Malkiel\'s "A Random Walk Down Wall '
                              'Street".'},
                  5: {"text": '@jidugger mostly got it right. It basically mean that past performance of a stock, '
                              'or a basket of stocks, are not at all useful when trying to predict its future. There '
                              'is no proven correlation between past and future performance. If there was such a '
                              'correlation, that was "proven" or known, then investors would quickly exploit this '
                              'correlation by buying or selling this stock, thus nullifying the prediction. It '
                              'doesn\'t mean the specific individuals cannot predict the future stock market - hell, '
                              'if I set up 2^100 different robots, where every robots gives a different series of '
                              'answers to the 100 questions "how will stock X do Y days from now" (for 1<=Y<=100), '
                              'then one of those robots would be perfectly correct. The problem is that an outside '
                              'observer has no way of knowing which of the predictor robots is right. To say that '
                              'stock is memoryless strikes me as not quite right -- to   the extent that stocks are '
                              'valued based on earnings, much of what we   infer about future earnings relies on past '
                              'and present earnings. To put it another way - you have $1000 now, and need to decide '
                              'whether to invest in a particular stock, or a stock index. The "memoryless" property '
                              'means that no matter how many earning reports you view ... by the time you see them, '
                              'the stock price already accounts for them, so they\'re not useful to you. If the '
                              'earning reports are positive, the stock is already "too high" because people bought it '
                              'before you did. So on average, you can\'t use this information to predict the stock\'s '
                              'future performance, and are better off investing in an index fund (unless you desire '
                              'extra risk that doesn\'t come with more profitability).'},
                  6: {"text": 'It means price movements in the past do not affect price movements in the future. '
                              'Think of the situation of a coin, if you flip it once, and then you flip it a second '
                              'time, the results are independent of each other. If the first time, you flipped a '
                              'HEAD, it does not mean that the coin will remember it, and produce a TAIL the second '
                              'time. This is the meaning of "memoryless". FYI, stock markets are clearly not '
                              'memoryless. It is just an assumption for academic purposes.'},
                  7: {"text": 'It means price movements in the past do not affect price movements in the future. '
                              'Think of the situation of a coin, if you flip it once, and then you flip it a second '
                              'time, the results are independent of each other. If the first time, you flipped a '
                              'HEAD, it does not mean that the coin will remember it, and produce a TAIL the second '
                              'time. This is the meaning of "memoryless". FYI, stock markets are clearly not '
                              'memoryless. It is just an assumption for academic purposes.'}
                  }
    match_meta_json = json.dumps(match_meta, sort_keys=True)

    pretrained_model = 'models/bert-qa'
    model_path = "models/2_finbert-qa-50_512_16_3e6.pt"

    ranker = FinBertQARanker(pretrained_model_name_or_path=pretrained_model, model_path=model_path)
    ranker.batch_size = batch_size

    new_scores = ranker.score(
        query_meta,
        old_match_scores,
        match_meta
    )

    np.testing.assert_approx_equal(new_scores[0][1], 0.9864102, significant=4)
    np.testing.assert_approx_equal(new_scores[1][1], 0.9815844, significant=4)
    np.testing.assert_approx_equal(new_scores[2][1], 0.97208554, significant=4)
    np.testing.assert_approx_equal(new_scores[3][1], 0.99254483, significant=4)
    np.testing.assert_approx_equal(new_scores[4][1], 0.9920474, significant=4)
    np.testing.assert_approx_equal(new_scores[5][1], 0.9882311, significant=4)
    np.testing.assert_approx_equal(new_scores[6][1], 0.9882311, significant=4)

    # Guarantee no side-effects happen
    assert query_meta_json == json.dumps(query_meta, sort_keys=True)
    assert old_match_scores_json == json.dumps(old_match_scores, sort_keys=True)
    assert match_meta_json == json.dumps(match_meta, sort_keys=True)
