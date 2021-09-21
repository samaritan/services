import logging

from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy

from .helper import Helper
from .schemas import ChangeSchema, FunctionChurnSchema, ProjectSchema

METRIC = 'functionchurn'
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


class FunctionChurnService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    parser_rpc = RpcProxy('parser')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        project = ProjectSchema().load(project)
        if self.parser_rpc.is_supported(project.language):
            project = ProjectSchema().dump(project)
            change = self._get_change(project, sha, path)
            helper = Helper(project, self.repository_rpc, self.parser_rpc)
            functionchurn = helper.collect(sha, change)
            return FunctionChurnSchema().dump(functionchurn)
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
