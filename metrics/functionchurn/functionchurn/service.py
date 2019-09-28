import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .helper import Helper
from .schemas import ChangesSchema, FunctionChurnSchema, ProjectSchema

logger = logging.getLogger(__name__)


class FunctionChurnService:
    name = 'functionchurn'

    config = Config()
    parser_rpc = RpcProxy('parser')
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        functionchurn = list()
        project = ProjectSchema().load(self.project_rpc.get(project))
        if self.parser_rpc.is_supported(project.language):
            changes = self._get_changes(project)
            helper = Helper(project, self.repository_rpc, self.parser_rpc)
            functionchurn = helper.collect(changes)
        return FunctionChurnSchema(many=True).dump(functionchurn)

    def _get_changes(self, project):
        changes = self.repository_rpc.get_changes(project.name)
        return ChangesSchema(many=True).load(changes)
