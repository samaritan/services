import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Churn
from .schemas import DeltasSchema, ChurnSchema

logger = logging.getLogger(__name__)


class ChurnService:
    name = 'churn'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        deltas = self.repository_rpc.get_deltas(project, processes)
        deltas = DeltasSchema(many=True).load(deltas)

        churn = list()
        for delta in deltas:
            commit = delta.commit
            churn.extend([
                Churn(commit, path, d.insertions, d.deletions)
                for (path, d) in delta.deltas.items()
            ])

        return ChurnSchema(many=True).dump(churn)
