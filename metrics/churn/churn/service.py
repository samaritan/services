import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Churn, LineChurn
from .schemas import DeltasSchema, ChurnSchema, ProjectSchema

logger = logging.getLogger(__name__)


class ChurnService:
    name = 'churn'

    config = Config()
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project))

        deltas = self.repository_rpc.get_deltas(project.name, processes)
        deltas = DeltasSchema(many=True).load(deltas)

        churn = list()
        for delta in deltas:
            commit = delta.commit
            churn.extend([
                Churn(commit, path, LineChurn(d.insertions, d.deletions), None)
                for (path, d) in delta.deltas.items()
            ])

        return ChurnSchema(many=True).dump(churn)
