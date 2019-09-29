import logging
import os

from eventlet.greenpool import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from . import utilities
from .patchtokens import get_patchtokens
from .schemas import PatchSchema, PatchTokensSchema

logger = logging.getLogger(__name__)


def _get_patches(project, commits, repository_rpc):
    return repository_rpc.get_patches(project, commits)


class PatchTokensService:
    name = 'patchtokens'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, **options):
        logger.debug(project)

        patches = self._get_patches(project)
        patchtokens = get_patchtokens(patches)
        return PatchTokensSchema().dump(patchtokens)

    def _get_patches(self, project):
        commits = self.repository_rpc.get_commits(project)
        chunks = utilities.chunk(commits, size=round(len(commits) * 0.01))

        pool = GreenPool(os.cpu_count())
        arguments = [(project, c, self.repository_rpc) for c in chunks]
        patches = list()
        for _patches in pool.starmap(_get_patches, arguments):
            patches.extend(_patches)
        return PatchSchema(many=True).load(patches)
