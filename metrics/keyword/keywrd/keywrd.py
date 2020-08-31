import logging

from sklearn.feature_extraction.text import CountVectorizer
from .models import Keyword

logger = logging.getLogger(__name__)


class Keywrd:
    def __init__(self, keywords):
        self._vectorizer = CountVectorizer(vocabulary=keywords)

    def get(self, patch):
        features = self._vectorizer.get_feature_names()
        vectors = self._vectorizer.transform([patch.patch])

        commit = patch.commit
        vector = vectors.getrow(0).tocoo()
        keyword = Keyword(
            commit=commit,
            keyword={
                features[c]: d.item()
                for c, d in zip(vector.col, vector.data)
            }
        )
        return keyword
