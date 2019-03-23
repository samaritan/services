import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .schemas import DeveloperSchema

logger = logging.getLogger(__name__)


class ContributorService:
    name = 'contributor'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        developers = self.repository_rpc.get_developers(project, processes)
        developers = DeveloperSchema(many=True).load(developers).data

        return len(developers)
