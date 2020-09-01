import logging

from eventlet.greenpool import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .patchtokens import get_patchtokens
from .schemas import CommitSchema, PatchSchema, PatchTokensSchema

logger = logging.getLogger(__name__)


def _get_patch(project, commit, repository_rpc):
    return repository_rpc.get_patch(project, commit.sha)


class PatchTokensService:
    name = 'patchtokens'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha=None, **options):
        logger.debug(project)

        patches = self._get_patches(project, sha)
        patchtokens = get_patchtokens(patches)
        return PatchTokensSchema().dump(patchtokens)

    def _get_patches(self, project, sha):
        commits = None
        if sha is None:
            commits = self.repository_rpc.get_commits(project)
        else:
            commits = [self.repository_rpc.get_commit(project, sha)]
        commits = CommitSchema(many=True).load(commits)

        pool = GreenPool()
        arguments = ((project, c, self.repository_rpc) for c in commits)
        patches = list()
        for item in pool.starmap(_get_patch, arguments):
            patches.append(item)

        return PatchSchema(many=True).load(patches)
