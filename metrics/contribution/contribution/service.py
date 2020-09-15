import logging

from eventlet import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .contribution import get_contribution
from .schemas import ChangesSchema, CommitSchema, ContributionSchema

logger = logging.getLogger(__name__)


def _get_changes(project, commit, repository_rpc):
    changes = repository_rpc.get_changes(project, commit.sha)
    return ChangesSchema(many=True).load(changes)


class ContributionService:
    name = 'contribution'

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

        contribution = get_contribution(changes, **options)
        return ContributionSchema(many=True).dump(contribution)
