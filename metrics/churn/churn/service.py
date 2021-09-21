import logging

from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy

from .models import Churn
from .schemas import DeltaSchema, ChurnSchema

METRIC = 'churn'
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


class ChurnService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        delta = self._get_delta(project, sha, path)
        insertions, deletions = delta.insertions, delta.deletions

        churn = None
        if insertions is not None and deletions is not None:
            churn = Churn(insertions, deletions, insertions + deletions)
        return ChurnSchema().dump(churn) if churn is not None else None

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        sha = payload.get('sha')
        path = payload.get('path')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(project, sha, path, **options)
        self.publish(payload, routing_key='measure')

    def _get_delta(self, project, sha, path):
        delta = self.repository_rpc.get_delta(project, sha, path)
        return DeltaSchema().load(delta)
