import logging
import os

from eventlet.greenpool import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import ChangeType, RelativeChurn
from .schemas import ChangesSchema, ChurnSchema, RelativeChurnSchema

logger = logging.getLogger(__name__)


def _get_relativechurn(project, churn, changes, repository_rpc):
    commit, path = churn.commit, churn.path
    insertions, deletions = churn.insertions, churn.deletions
    change = changes[(commit, path)]

    if change.type == ChangeType.ADDED:
        insertions, deletions = 1.0, 0.0
    elif change.type == ChangeType.DELETED:
        insertions, deletions = None, None
    else:
        size = repository_rpc.get_size(project, change.oids.after)
        if size is not None:
            insertions = insertions / size if insertions is not None else None
            deletions = deletions / size if deletions is not None else None
    return RelativeChurn(commit, path, insertions, deletions)


class RelativeChurnService:
    name = 'relativechurn'

    config = Config()
    churn_rpc = RpcProxy('churn')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path=None, **options):
        logger.debug(project)

        changes = self._get_changes(project, sha, path)
        churn = self._get_churn(project, sha, path)

        pool = GreenPool(os.cpu_count())
        arguments = [(project, c, changes, self.repository_rpc) for c in churn]
        relativechurn = list()
        for item in pool.starmap(_get_relativechurn, arguments):
            relativechurn.append(item)
        return RelativeChurnSchema(many=True).dump(relativechurn)

    def _get_changes(self, project, sha, path):
        changes = self.repository_rpc.get_changes(project, sha, path)
        changes = ChangesSchema(many=True).load(changes)
        changes = {
            (c.commit, p): cc for c in changes for p, cc in c.changes.items()
        }
        return changes

    def _get_churn(self, project, sha, path):
        churn = self.churn_rpc.collect(project, sha, path)
        return ChurnSchema(many=True).load(churn)
