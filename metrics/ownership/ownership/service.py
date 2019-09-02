import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .ownership import get_ownership
from .schemas import CommitSchema, OwnershipSchema

logger = logging.getLogger(__name__)


class OwnershipService:
    name = 'ownership'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        commits = self.repository_rpc.get_commits(project, processes)
        commits = CommitSchema(many=True).load(commits)
        ownerships = get_ownership(commits)
        return OwnershipSchema(many=True).dump(ownerships)
