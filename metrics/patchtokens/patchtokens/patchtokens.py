import logging

from sklearn.feature_extraction.text import CountVectorizer

from .models import PatchTokens

logger = logging.getLogger(__name__)


def get_patchtokens(patch):
    vectorizer = CountVectorizer(binary=True)
    vectorizer.fit([patch.patch])
    tokens = vectorizer.get_feature_names()
    return PatchTokens(commit=patch.commit, tokens=tokens)
