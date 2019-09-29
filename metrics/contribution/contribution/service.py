import logging

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
    def collect(self, project, **options):
        logger.debug(project)

        changes = self.repository_rpc.get_changes(project)
        changes = ChangesSchema(many=True).load(changes)

        contribution = get_contribution(changes, **options)
        return ContributionSchema(many=True).dump(contribution)
