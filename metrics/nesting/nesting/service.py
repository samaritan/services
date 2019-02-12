import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Nesting
from .schemas import NestingSchema, MetricsSchema

logger = logging.getLogger(__name__)
METRICS = ['MaxNesting']

def _transform(metrics):
    nestings = list()
    for item in metrics:
        entity = item.entity
        nesting = item.metrics['MaxNesting']
        if nesting is not None:
            nestings.append(Nesting(entity=entity, nesting=nesting))
    return nestings


class ComplexityService:
    name = 'nesting'

    config = Config()
    understand_rpc = RpcProxy('understand')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)
        metrics = self.understand_rpc.get_metrics(project, METRICS)
        metrics = MetricsSchema(many=True).load(metrics).data
        return NestingSchema(many=True).dump(_transform(metrics)).data
