import logging
import os

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
        for _change in change.changes:
            _pastchanges = paths.get(_change.path, 0)
            pastchanges.append(PastChanges(
                commit=commit, path=_change.path, pastchanges=_pastchanges
            ))
            paths[_change.path] = _pastchanges + 1

    return pastchanges


class PastChangesService:
    name = 'pastchanges'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        changes = self.repository_rpc.get_changes(project, processes)
        changes = ChangesSchema(many=True).load(changes).data
        pastchanges = _get_pastchanges(changes)

        return PastChangesSchema(many=True).dump(pastchanges).data
