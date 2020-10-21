import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .schemas import CommitSchema

logger = logging.getLogger(__name__)


def _get_filter(name, email):
    def _filter(item):
        return item.author.name == name and item.author.email == email
    return _filter


class OwnershipService:
    name = 'ownership'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, name, email, **options):
        logger.debug(project)

        commits = self.repository_rpc.get_commits(project, sha)
        commits = CommitSchema(many=True).load(commits)
        ownership = len(list(filter(_get_filter(name, email), commits))) / \
            len(commits)
        return ownership
