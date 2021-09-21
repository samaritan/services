import logging

from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy

from .models import ChangeType, RelativeChurn
from .schemas import ChangeSchema, ChurnSchema, RelativeChurnSchema

METRIC = 'relativechurn'
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


class RelativeChurnService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    churn_rpc = RpcProxy('churn')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        change = self._get_change(project, sha, path)
        churn = self._get_churn(project, sha, path)

        if churn is not None:
            relativechurn = self._get_relativechurn(project, churn, change)
            return RelativeChurnSchema().dump(relativechurn)
        return None

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        sha = payload.get('sha')
        path = payload.get('path')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(project, sha, path, **options)
        self.publish(payload, routing_key='measure')

    def _get_change(self, project, sha, path):
        change = self.repository_rpc.get_change(project, sha, path)
        return ChangeSchema().load(change)

    def _get_churn(self, project, sha, path):
        churn = self.churn_rpc.collect(project, sha, path)
        return ChurnSchema().load(churn) if churn is not None else None

    def _get_relativechurn(self, project, churn, change):
        if change.type == ChangeType.ADDED:
            return RelativeChurn(1.0, 0.0, 1.0)

        if change.type == ChangeType.DELETED:
            insertions, deletions, aggregate = None, None, None
            return RelativeChurn(None, None, None)

        size = self.repository_rpc.get_size(project, change.oids.after)
        insertions = churn.insertions / size
        deletions = churn.deletions / size
        aggregate = churn.aggregate / size
        return RelativeChurn(insertions, deletions, aggregate)
