from collections import namedtuple
from enum import Enum
from typing import Dict, List, Optional

import spacy
from jina.executors.rankers import Match2DocRanker

NEREntity = namedtuple('NEREntity', ('value', 'type'))


class EntityMatchEnum(Enum):
    NONE = 0  # no match
    TYPE = 1  # matches on same type but diff value
    FULL = 2  # same type and same value
    FULL_ALL = 3  # all of them match


class NERSpacyRanker(Match2DocRanker):
    # TODO docstring
    def __init__(
        self,
        model='en_core_web_lg',
        factor_type_match=1.1,
        factor_full_match=1.4,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.model = model
        self.factor_full_match = factor_full_match
        self.factor_type_match = factor_type_match

    def post_init(self):
        """Init the Spacy model"""
        super(NERSpacyRanker, self).post_init()
        try:
            self.nlp = spacy.load(self.model)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(
                f'{self.model} was not found. Please make sure you either install it or train it and provide it yourself'
            )

    def score(
        self,
        old_matches_scores: List[List[float]],
        queries_metas: List[Dict],
        matches_metas: List[List[Dict]],
    ) -> List[List[float]]:
        """Calculate the negative Levenshtein distance

        :param old_matches_scores: Contains old scores in a list
        :param queries_metas: Dictionary containing all the query meta information requested by the `query_required_keys` class_variable.
        :param matches_metas: List containing all the matches meta information requested by the `match_required_keys` class_variable. Sorted in the same way as `old_match_scores`
        :return: An iterable of the new scores
        """
        return [
            self._recalc_score_matches(matches_metas[i], old_matches_scores[i], query_meta)
            for i, query_meta in enumerate(queries_metas)
        ]

    def _recalc_score_matches(self, matches_metas, old_matches_scores, query_meta):
        query_ents = [NEREntity(value=e.text, type=e.label_) for e in self.nlp(query_meta['text'].strip()).ents]
        new_scores = []
        # TODO design formula for recalculating score

        for match_score, match in zip(old_matches_scores, matches_metas):
            match_ents = [NEREntity(value=e.text, type=e.label_) for e in self.nlp(match['text'].strip()).ents]
            entity_match_type = self._entity_match(match_ents, query_ents)

            new_match_score = self._recalc_match_score(match_score, entity_match_type)
            print(
                f'#### match text = {match["text"].strip()}; orig score = {match_score}; new score = {new_match_score}; match type = {entity_match_type}'
            )
            new_scores.append(new_match_score)

        return new_scores

    def _entity_match(self, match_ents: List[NEREntity], query_ents: List[NEREntity]) -> int:
        ner_matches = []
        match_ents_types = [m.type for m in match_ents]
        for q_e in query_ents:
            if q_e in match_ents:
                ner_matches.append(EntityMatchEnum.FULL.value)
            else:
                if q_e.type in match_ents_types:
                    ner_matches.append(EntityMatchEnum.TYPE.value)
                else:
                    ner_matches.append(EntityMatchEnum.NONE.value)

        # TODO better formula
        return max(ner_matches)

    def _recalc_match_score(self, match_score, entity_match: int):
        if entity_match == EntityMatchEnum.NONE.value:
            return match_score
        elif entity_match == EntityMatchEnum.TYPE.value:
            return match_score * self.factor_type_match
        elif entity_match == EntityMatchEnum.FULL.value:
            return match_score * self.factor_full_match
