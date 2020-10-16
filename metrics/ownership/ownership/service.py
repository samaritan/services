import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .ownership import get_ownership
from .schemas import CommitSchema, OwnershipSchema

logger = logging.getLogger(__name__)


def _get_filter(name, email):
    def _filter(item):
        return item.developer.name == name and item.developer.email == email
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
        ownerships = get_ownership(commits)
        for ownership in filter(_get_filter(name, email), ownerships):
            return OwnershipSchema().dump(ownership)
        return None
