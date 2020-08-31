import logging

from eventlet import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .hunk import get_hunk
from .schemas import CommitSchema, HunkSchema, PatchSchema

logger = logging.getLogger(__name__)


def _get_hunks(project, commit, repository_rpc):
    patch = repository_rpc.get_patch(project, commit.sha)
    patch = PatchSchema().load(patch)
    return get_hunk(patch)


class HunkService:
    name = 'hunk'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha=None, **options):
        logger.debug(project)

        commits = None
        if sha is None:
            commits = self.repository_rpc.get_commits(project)
        else:
            commits = [self.repository_rpc.get_commit(project, sha)]
        commits = CommitSchema(many=True).load(commits)

        pool = GreenPool()
        arguments = ((project, c, self.repository_rpc) for c in commits)
        hunks = list()
        for item in pool.starmap(_get_hunks, arguments):
            hunks.append(item)

        return HunkSchema(many=True).dump(hunks)
