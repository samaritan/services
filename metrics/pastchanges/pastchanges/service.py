import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .schemas import CommitSchema

logger = logging.getLogger(__name__)


class PastChangesService:
    name = 'pastchanges'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        commits = self.repository_rpc.get_commits(project, sha, path)

        commit = self.repository_rpc.get_commit(project, sha)
        commit = CommitSchema().load(commit)

        return len(commits) - 1 if commits else 0
