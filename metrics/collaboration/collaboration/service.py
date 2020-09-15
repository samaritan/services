import logging

from eventlet import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .collaboration import get_collaboration
from .schemas import ChangesSchema, CollaborationSchema, CommitSchema

logger = logging.getLogger(__name__)


def _get_changes(project, commit, repository_rpc):
    changes = repository_rpc.get_changes(project, commit.sha)
    return ChangesSchema(many=True).load(changes)


class CollaborationService:
    name = 'collaboration'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, **options):
        logger.debug(project)

        commits = self.repository_rpc.get_commits(project, sha)
        commits = CommitSchema(many=True).load(commits)

        pool = GreenPool()
        arguments = [(project, c, self.repository_rpc) for c in commits]
        changes = list()
        for item in pool.starmap(_get_changes, arguments):
            changes.extend(item)

        collaboration = get_collaboration(changes, **options)
        return CollaborationSchema(many=True).dump(collaboration)
