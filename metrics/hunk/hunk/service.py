import logging
import re

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .schemas import PatchSchema

HUNKHEADER_RE = re.compile(r'(?:\n@@)')
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

        return len(HUNKHEADER_RE.findall(patch.patch))
