import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import PastAuthors
from .schemas import ChangesSchema, PastAuthorsSchema

logger = logging.getLogger(__name__)


def _get_pastauthors(changes):
    pastauthors = list()

    # Assume changes from repository service are in reverse chronological order
    changes.reverse()

    paths = dict()
    for change in changes:
        commit = change.commit
        for path in change.changes:
            pauthors = paths.get(path, set()) - {commit.author}
            paths[path] = pauthors | {commit.author}
            pastauthors.append(PastAuthors(
                commit=commit, path=path, pastauthors=len(pauthors)
            ))

    return pastauthors


class PastAuthorsService:
    name = 'pastauthors'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        changes = self.repository_rpc.get_changes(project, processes)
        changes = ChangesSchema(many=True).load(changes)
        pastauthors = _get_pastauthors(changes)

        return PastAuthorsSchema(many=True).dump(pastauthors)
