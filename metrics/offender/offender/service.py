import logging

from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy

from .schemas import CommitSchema, OffenderSchema, ProjectSchema
from .offenders import get_offenders

METRIC = 'offender'
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


def _get_filter(commit):
    def _filter(item):
        return item.timestamp <= commit.timestamp
    return _filter


def _get_path_filter(path):
    def _filter(item):
        return (item.path == path or (item.aliases is not None and
                                      any(i == path for i in item.aliases)))
    return _filter


class OffenderService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        commit = self.repository_rpc.get_commit(project, sha)
        commit = CommitSchema().load(commit)

        project = ProjectSchema().load(project)

        offenders = OffenderSchema(many=True).load(get_offenders(project))
        offenders = filter(_get_filter(commit), offenders)
        offenders = filter(_get_path_filter(path), offenders)
        offenders = list(offenders)

        return len(offenders) > 0

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        sha = payload.get('sha')
        path = payload.get('path')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(project, sha, path, **options)
        self.publish(payload, routing_key='measure')
