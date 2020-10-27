import logging

from sklearn.feature_extraction.text import CountVectorizer

logger = logging.getLogger(__name__)


class Keywrd:
    def __init__(self, keywords):
        self._vectorizer = CountVectorizer(vocabulary=keywords)

    def get(self, patch):
        features = self._vectorizer.get_feature_names()
        vectors = self._vectorizer.transform([patch])
        vector = vectors.getrow(0).tocoo()
        return {features[c]: d.item() for c, d in zip(vector.col, vector.data)}
