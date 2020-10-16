import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import PastAuthors
from .schemas import CommitSchema, PastAuthorsSchema

logger = logging.getLogger(__name__)


class PastAuthorsService:
    name = 'pastauthors'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        commits = self.repository_rpc.get_commits(project, sha, path)
        commits = CommitSchema(many=True).load(commits)

        commit = self.repository_rpc.get_commit(project, sha)
        commit = CommitSchema().load(commit)

        pastauthors = len({c.author for c in commits} - {commit.author})
        pastauthors = PastAuthors(
            commit=commit, path=path, pastauthors=pastauthors
        )
        return PastAuthorsSchema().dump(pastauthors)
