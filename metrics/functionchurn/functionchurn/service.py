import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .helper import Helper
from .redis import Redis
from .schemas import ChangesSchema, FunctionChurnSchema, ProjectSchema

logger = logging.getLogger(__name__)


class FunctionChurnService:
    name = 'functionchurn'

    config = Config()
    redis = Redis()

    parser_rpc = RpcProxy('parser')
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project))
        if self.parser_rpc.is_supported(project.language):
            changes = self._get_changes(project, sha, path)
            helper = Helper(
                project, self.repository_rpc, self.parser_rpc, self.redis
            )
            for functionchurn in helper.collect(changes):
                return FunctionChurnSchema().dump(functionchurn)
        return None

    def _get_changes(self, project, sha, path):
        changes = self.repository_rpc.get_changes(project.name, sha, path)
        return ChangesSchema(many=True).load(changes)
