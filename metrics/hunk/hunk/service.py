import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .hunk import get_hunk
from .schemas import CommitSchema, HunkSchema, PatchSchema

logger = logging.getLogger(__name__)


class HunkService:
    name = 'hunk'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, **options):
        logger.debug(project)

        patch = self.repository_rpc.get_patch(project, sha)
        patch = PatchSchema().load(patch)
        hunk = get_hunk(patch)

        return HunkSchema().dump(hunk)
