import logging

from sklearn.feature_extraction.text import CountVectorizer

from .models import PatchTokens, PatchTokenIndices

logger = logging.getLogger(__name__)


def _get_patchtokenindices(matrix, index, patch):
    commit = patch.commit
    tokenindices = matrix.getrow(index).nonzero()[1].tolist()
    return PatchTokenIndices(commit=commit, patchtokenindices=tokenindices)


def get_patchtokens(patches):
    vectorizer = CountVectorizer(binary=True)
    matrix = vectorizer.fit_transform(p.patch for p in patches)
    tokens = vectorizer.get_feature_names()

    patchtokenindices = list()
    for (index, patch) in enumerate(patches):
        patchtokenindices.append(_get_patchtokenindices(matrix, index, patch))
    return PatchTokens(tokens=tokens, patchtokenindices=patchtokenindices)
