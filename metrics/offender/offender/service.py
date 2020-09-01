import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .schemas import CommitSchema, OffenderSchema
from .offenders import get_offenders

logger = logging.getLogger(__name__)


def _get_filter(commit):
    def _filter(item):
        return item.timestamp <= commit.timestamp
    return _filter


class OffenderService:
    name = 'offender'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha=None, **options):
        logger.debug(project)

        offenders = get_offenders(project)
        offenders = OffenderSchema(many=True).load(offenders)
        if sha is not None:
            commit = self.repository_rpc.get_commit(project, sha)
            commit = CommitSchema().load(commit)
            offenders = filter(_get_filter(commit), offenders)

        return OffenderSchema(many=True).dump(offenders)
