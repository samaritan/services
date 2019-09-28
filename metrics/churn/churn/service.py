import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .helper import Helper
from .schemas import DeltasSchema, ChangesSchema, ChurnSchema, ProjectSchema

logger = logging.getLogger(__name__)


class ChurnService:
    name = 'churn'

    config = Config()
    parser_rpc = RpcProxy('parser')
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project))
        changes = self._get_changes(project)
        deltas = self._get_deltas(project)
        helper = Helper(project, self.repository_rpc, self.parser_rpc)
        churn = helper.collect(changes, deltas)

        return ChurnSchema(many=True).dump(churn)

    def _get_changes(self, project):
        changes = list()
        if self.parser_rpc.is_supported(project.language):
            changes = self.repository_rpc.get_changes(project.name)
            changes = ChangesSchema(many=True).load(changes)
        return changes

    def _get_deltas(self, project):
        deltas = self.repository_rpc.get_deltas(project.name)
        return DeltasSchema(many=True).load(deltas)
