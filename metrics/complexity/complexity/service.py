import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Complexity
from .schemas import ComplexitySchema, MetricsSchema

logger = logging.getLogger(__name__)
METRICS = ['Cyclomatic']

def _transform(metrics):
    complexities = list()
    for item in metrics:
        entity = item.entity
        complexity = item.metrics['Cyclomatic']
        if entity.type == 'function' and complexity is not None:
            complexities.append(Complexity(
                entity=entity, complexity=complexity
            ))
    return complexities


class ComplexityService:
    name = 'complexity'

    config = Config()
    understand_rpc = RpcProxy('understand')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)
        metrics = self.understand_rpc.get_metrics(project, METRICS)
        metrics = MetricsSchema(many=True).load(metrics)
        return ComplexitySchema(many=True).dump(_transform(metrics))
