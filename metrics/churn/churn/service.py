import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Churn
from .schemas import ChangesSchema, ChurnSchema

logger = logging.getLogger(__name__)


class ChurnService:
    name = 'churn'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        changes = self.repository_rpc.get_changes(project, processes)
        changes = ChangesSchema(many=True).load(changes).data

        churn = list()
        for change in changes:
            commit = change.commit
            churn.extend([
                Churn(commit, c.path, c.insertions, c.deletions)
                for c in change.changes
            ])

        return ChurnSchema(many=True).dump(churn).data
