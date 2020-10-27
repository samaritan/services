import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Churn
from .schemas import DeltaSchema, ChurnSchema

logger = logging.getLogger(__name__)


class ChurnService:
    name = 'churn'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        delta = self._get_delta(project, sha, path)
        churn = Churn(delta.insertions, delta.deletions)
        return ChurnSchema().dump(churn)

    def _get_delta(self, project, sha, path):
        delta = self.repository_rpc.get_delta(project, sha, path)
        return DeltaSchema().load(delta)
