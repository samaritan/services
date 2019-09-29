import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from . import utilities
from .hunk import get_hunks
from .schemas import HunkSchema, PatchSchema

logger = logging.getLogger(__name__)


class HunkService:
    name = 'hunk'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, **options):
        logger.debug(project)

        hunks = list()
        commits = self.repository_rpc.get_commits(project)
        for chunk in utilities.chunk(commits, size=round(len(commits) * 0.05)):
            patches = self.repository_rpc.get_patches(project, chunk)
            patches = PatchSchema(many=True).load(patches)
            hunks.extend(get_hunks(patches))
            patches.clear()

        return HunkSchema(many=True).dump(hunks)
