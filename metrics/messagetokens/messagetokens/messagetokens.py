import logging

from sklearn.feature_extraction.text import CountVectorizer

from .models import MessageTokens

logger = logging.getLogger(__name__)


def get_messagetokens(message):
    vectorizer = CountVectorizer(binary=True)
    vectorizer.fit([message.message])
    tokens = vectorizer.get_feature_names()
    return MessageTokens(commit=message.commit, tokens=tokens)
