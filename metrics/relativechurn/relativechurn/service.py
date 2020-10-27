import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import ChangeType, RelativeChurn
from .schemas import ChangeSchema, ChurnSchema, RelativeChurnSchema

logger = logging.getLogger(__name__)


def _get_relativechurn(project, churn, change, repository_rpc):
    insertions, deletions = churn.insertions, churn.deletions

    if change.type == ChangeType.ADDED:
        insertions, deletions = 1.0, 0.0
    elif change.type == ChangeType.DELETED:
        insertions, deletions = None, None
    else:
        size = repository_rpc.get_size(project, change.oids.after)
        if size is not None:
            insertions = insertions / size if insertions is not None else None
            deletions = deletions / size if deletions is not None else None
    return RelativeChurn(insertions, deletions)


class RelativeChurnService:
    name = 'relativechurn'

    config = Config()
    churn_rpc = RpcProxy('churn')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        change = self._get_change(project, sha, path)
        churn = self._get_churn(project, sha, path)

        relativechurn = _get_relativechurn(
            project, churn, change, self.repository_rpc
        )
        return RelativeChurnSchema().dump(relativechurn)

    def _get_change(self, project, sha, path):
        change = self.repository_rpc.get_change(project, sha, path)
        return ChangeSchema().load(change)

    def _get_churn(self, project, sha, path):
        churn = self.churn_rpc.collect(project, sha, path)
        return ChurnSchema().load(churn)
