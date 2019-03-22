import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .ownership import get_ownership
from .schemas import CommitSchema, OwnershipSchema, ProjectSchema

logger = logging.getLogger(__name__)


class OwnershipService:
    name = 'ownership'

    config = Config()
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project)).data
        commits = self.repository_rpc.get_commits(project.name, processes)
        commits = CommitSchema(many=True).load(commits).data
        ownerships = get_ownership(commits)
        return OwnershipSchema(many=True).dump(ownerships).data
