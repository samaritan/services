import logging
import operator

from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy

from .models import Flow
from .schemas import FlowSchema, MetricsSchema

METRIC = 'flow'
METRICS = ['CountInput', 'CountOutput', 'CountPath']
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)

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


class FlowService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    understand_rpc = RpcProxy('understand')

    @rpc
    def collect(self, project, **options):
        logger.debug(project)
        metrics = self.understand_rpc.get_metrics(project, METRICS)
        metrics = MetricsSchema(many=True).load(metrics)
        return FlowSchema(many=True).dump(_transform(metrics))

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(project, **options)
        self.publish(payload, routing_key='measure')
