import logging

from sklearn.feature_extraction.text import CountVectorizer
from .models import Keyword

logger = logging.getLogger(__name__)


def get_keywords(patches, keywords):
    _keywords = list()

    vectorizer = CountVectorizer(vocabulary=keywords)
    features = vectorizer.get_feature_names()
    vectors = vectorizer.transform([p.patch for p in patches])

    for index, patch in enumerate(patches):
        commit = patch.commit
        vector = vectors.getrow(index).tocoo()
        _keywords.append(Keyword(
            commit=commit,
            keyword={
                features[c]: d.item() for c, d in zip(vector.col, vector.data)
            }
        ))

    return _keywords
