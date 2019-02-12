import logging
import operator
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Flow
from .schemas import FlowSchema, MetricsSchema

logger = logging.getLogger(__name__)
METRICS = ['CountInput', 'CountOutput', 'CountPath']

def _transform(metrics):
    flows = list()
    itemgetter = operator.itemgetter(*METRICS)
    for item in metrics:
        entity = item.entity
        (ninput, noutput, npath) = itemgetter(item.metrics)
        if ninput is not None or noutput is not None or npath is not None:
            flows.append(Flow(
                entity=entity, ninput=ninput, noutput=noutput, npath=npath
            ))
    return flows


class ComplexityService:
    name = 'flow'

    config = Config()
    understand_rpc = RpcProxy('understand')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)
        metrics = self.understand_rpc.get_metrics(project, METRICS)
        metrics = MetricsSchema(many=True).load(metrics).data
        return FlowSchema(many=True).dump(_transform(metrics)).data
