import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Churn
from .schemas import DeltasSchema, ChurnSchema

logger = logging.getLogger(__name__)


def _get_churn(deltas):
    deltas = ((d.commit, p, dd) for d in deltas for p, dd in d.deltas.items())
    for commit, path, delta in deltas:
        yield Churn(commit, path, delta.insertions, delta.deletions)


class ChurnService:
    name = 'churn'

    config = Config()
    parser_rpc = RpcProxy('parser')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path=None, **options):
        logger.debug(project)

        deltas = self._get_deltas(project, sha, path)
        return ChurnSchema(many=True).dump(_get_churn(deltas))

    def _get_deltas(self, project, sha, path):
        deltas = self.repository_rpc.get_deltas(project, sha, path)
        return DeltasSchema(many=True).load(deltas)
