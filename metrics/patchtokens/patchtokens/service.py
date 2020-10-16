import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .patchtokens import get_patchtokens
from .schemas import PatchSchema, PatchTokensSchema

logger = logging.getLogger(__name__)


class PatchTokensService:
    name = 'patchtokens'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, **options):
        logger.debug(project)

        patch = self.repository_rpc.get_patch(project, sha)
        patch = PatchSchema().load(patch)
        patchtokens = get_patchtokens(patch)

        return PatchTokensSchema().dump(patchtokens)
