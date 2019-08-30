import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .contribution import get_contribution
from .schemas import ChangesSchema, ContributionSchema

logger = logging.getLogger(__name__)


class ContributionService:
    name = 'contribution'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        changes = self.repository_rpc.get_changes(project, processes)
        changes = ChangesSchema(many=True).load(changes)

        contribution = get_contribution(changes, processes, **options)
        return ContributionSchema(many=True).dump(contribution)
