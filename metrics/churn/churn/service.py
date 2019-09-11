import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .helpers import ChurnHelper
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

        deltas = self._get_deltas(project)

        helper = ChurnHelper(project, self.repository_rpc)
        churn = list(helper.collect(deltas))
        return ChurnSchema(many=True).dump(churn)

    def _get_deltas(self, project):
        deltas = self.repository_rpc.get_deltas(project.name)
        return DeltasSchema(many=True).load(deltas)
