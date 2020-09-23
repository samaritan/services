import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .ownership import get_ownership
from .schemas import CommitSchema, OwnershipSchema

logger = logging.getLogger(__name__)


def _get_name_filter(name):
    def _filter(value):
        return value.developer.name == name
    return _filter


def _get_email_filter(email):
    def _filter(value):
        return value.developer.email == email
    return _filter


class OwnershipService:
    name = 'ownership'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, name=None, email=None, **options):
        logger.debug(project)

        commits = self.repository_rpc.get_commits(project, sha)
        commits = CommitSchema(many=True).load(commits)
        ownerships = get_ownership(commits)

        if name is not None:
            ownerships = filter(_get_name_filter(name), ownerships)
        if email is not None:
            ownerships = filter(_get_email_filter(email), ownerships)

        return OwnershipSchema(many=True).dump(ownerships)
