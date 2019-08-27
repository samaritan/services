import logging

from sklearn.feature_extraction.text import CountVectorizer
from .models import Keyword

logger = logging.getLogger(__name__)


class Keywrd:
    def __init__(self, keywords):
        self._vectorizer = CountVectorizer(vocabulary=keywords)

    def get(self, patches):
        keywords = list()

        features = self._vectorizer.get_feature_names()
        vectors = self._vectorizer.transform([p.patch for p in patches])
        for index, patch in enumerate(patches):
            commit = patch.commit
            vector = vectors.getrow(index).tocoo()
            keyword = Keyword(
                commit=commit,
                keyword={
                    features[c]: d.item()
                    for c, d in zip(vector.col, vector.data)
                }
            )
            keywords.append(keyword)

        return keywords
