import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import PastChanges
from .schemas import CommitSchema, PastChangesSchema

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

        pastchanges = len(commits) - 1 if commits else 0
        pastchanges = PastChanges(
            commit=commit, path=path, pastchanges=pastchanges
        )
        return PastChangesSchema().dump(pastchanges)
