import logging
import os

from eventlet.greenpool import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from . import utilities
from .patchtokens import get_patchtokens
from .schemas import PatchSchema, PatchTokensSchema, ProjectSchema

logger = logging.getLogger(__name__)


def _get_patches(project, commits, repository_rpc):
    return repository_rpc.get_patches(project.name, commits)


class PatchTokensService:
    name = 'patchtokens'

    config = Config()
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project)).data
        patches = self._get_patches(project)
        patchtokens = get_patchtokens(patches)
        return PatchTokensSchema().dump(patchtokens).data

    def _get_patches(self, project):
        commits = self.repository_rpc.get_commits(project.name)
        chunks = utilities.chunk(commits, size=round(len(commits) * 0.01))

        pool = GreenPool(os.cpu_count())
        arguments = [(project, c, self.repository_rpc) for c in chunks]
        patches = list()
        for _patches in pool.starmap(_get_patches, arguments):
            patches.extend(_patches)
        return PatchSchema(many=True).load(patches).data
