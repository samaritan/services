import logging
import operator

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .models import Loc
from .schemas import LocSchema, MetricsSchema

logger = logging.getLogger(__name__)
METRICS = ['CountLineBlank', 'CountLineComment', 'CountLineCode']

def _transform(metrics):
    locs = list()
    itemgetter = operator.itemgetter(*METRICS)
    for item in metrics:
        entity = item.entity
        (bloc, cloc, sloc) = itemgetter(item.metrics)
        if bloc is not None or cloc is not None or sloc is not None:
            locs.append(Loc(entity=entity, bloc=bloc, cloc=cloc, sloc=sloc))
    return locs


class LocService:
    name = 'loc'

    config = Config()
    understand_rpc = RpcProxy('understand')

    @rpc
    def collect(self, project, **options):
        logger.debug(project)
        metrics = self.understand_rpc.get_metrics(project, METRICS)
        metrics = MetricsSchema(many=True).load(metrics)
        return LocSchema(many=True).dump(_transform(metrics))
