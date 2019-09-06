import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .churn import get_churn
from .schemas import DeltasSchema, ChurnSchema, ProjectSchema

logger = logging.getLogger(__name__)


class ChurnService:
    name = 'churn'

    config = Config()
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project))

        deltas = self.repository_rpc.get_deltas(project.name, processes)
        deltas = DeltasSchema(many=True).load(deltas)

        churn = list(get_churn(deltas))
        return ChurnSchema(many=True).dump(churn)
