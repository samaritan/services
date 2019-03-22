import collections
import logging

from .models import Ownership

logger = logging.getLogger(__name__)


def get_ownership(commits):
    ownerships = list()

    counter = collections.Counter([commit.author for commit in commits])
    for author, ncommit in counter.items():
        ownership = ncommit / len(commits)
        ownerships.append(Ownership(developer=author, ownership=ownership))

    return ownerships
