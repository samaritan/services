import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Entity, Metrics
from .schemas import MetricsSchema, ProjectSchema
from .udb import UDB

logger = logging.getLogger(__name__)


def _get_metrics(udb, metrics):
    metrics = udb.get_metrics(metrics)
    if not metrics:
        return None

    metricslist = list()
    for ((uid, name, type_, _path), _metrics) in metrics:
        metricslist.append(Metrics(
            entity=Entity(uid=uid, name=name, type=type_, path=_path),
            metrics=_metrics
        ))
    return metricslist


class UnderstandService:
    name = 'understand'

    config = Config()
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def get_metrics(self, project, metrics):
        logger.debug(project)
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        path = self.repository_rpc.get_path(project.name)
        udb = UDB(self._get_udbpath(project), project.language, path)
        return MetricsSchema(many=True).dump(_get_metrics(udb, metrics)).data

    def _get_udbpath(self, project):
        name = f'{project.name}.udb'
        return os.path.join(self.config['UNDERSTAND_ROOT'], name)
