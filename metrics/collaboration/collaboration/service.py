import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .collaboration import get_collaboration
from .schemas import ChangesSchema, CollaborationSchema

logger = logging.getLogger(__name__)


class CollaborationService:
    name = 'collaboration'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, **options):
        logger.debug(project)

        changes = self.repository_rpc.get_changes(project)
        changes = ChangesSchema(many=True).load(changes)

        collaboration = get_collaboration(changes, **options)
        return CollaborationSchema(many=True).dump(collaboration)
