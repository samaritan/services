import logging

from sklearn.feature_extraction.text import CountVectorizer

from .models import MessageTokens, MessageTokenIndices

logger = logging.getLogger(__name__)


def _get_messagetokenindices(matrix, index, message):
    commit = message.commit
    tokenindices = matrix.getrow(index).nonzero()[1].tolist()
    return MessageTokenIndices(commit=commit, messagetokenindices=tokenindices)


def get_messagetokens(messages):
    vectorizer = CountVectorizer(binary=True)
    matrix = vectorizer.fit_transform(m.message for m in messages)
    tokens = vectorizer.get_feature_names()

    messagetokenindices = list()
    for (index, message) in enumerate(messages):
        _messagetokenindices = _get_messagetokenindices(matrix, index, message)
        messagetokenindices.append(_messagetokenindices)

    return MessageTokens(
        tokens=tokens, messagetokenindices=messagetokenindices
    )
