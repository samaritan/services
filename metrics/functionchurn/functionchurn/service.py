import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .helper import Helper
from .schemas import ChangeSchema, FunctionChurnSchema, ProjectSchema

logger = logging.getLogger(__name__)


class FunctionChurnService:
    name = 'functionchurn'

    config = Config()

    parser_rpc = RpcProxy('parser')
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project))
        if self.parser_rpc.is_supported(project.language):
            change = self._get_change(project, sha, path)
            helper = Helper(project, self.repository_rpc, self.parser_rpc)
            functionchurn = helper.collect(sha, change)
            return FunctionChurnSchema().dump(functionchurn)
        return None

    def _get_change(self, project, sha, path):
        change = self.repository_rpc.get_change(project.name, sha, path)
        return ChangeSchema().load(change)
