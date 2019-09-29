import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import PastChanges
from .schemas import ChangesSchema, PastChangesSchema

logger = logging.getLogger(__name__)


def _get_pastchanges(changes):
    pastchanges = list()

    # Assume changes from repository service are in reverse chronological order
    changes.reverse()

    paths = dict()
    for change in changes:
        commit = change.commit
        for path in change.changes:
            pchanges = paths.get(path, 0)
            paths[path] = pchanges + 1
            pastchanges.append(PastChanges(
                commit=commit, path=path, pastchanges=pchanges
            ))

    return pastchanges


class PastChangesService:
    name = 'pastchanges'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, **options):
        logger.debug(project)

        changes = self.repository_rpc.get_changes(project)
        changes = ChangesSchema(many=True).load(changes)
        pastchanges = _get_pastchanges(changes)

        return PastChangesSchema(many=True).dump(pastchanges)
