import logging

from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy

from .schemas import CommitSchema

METRIC = 'ownership'
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


def _get_filter(name, email):
    def _filter(item):
        return item.author.name == name and item.author.email == email
    return _filter


class OwnershipService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, name, email, **options):
        logger.debug(project)

        commits = self.repository_rpc.get_commits(project, sha)
        commits = CommitSchema(many=True).load(commits)
        ownership = len(list(filter(_get_filter(name, email), commits))) / \
            len(commits)
        return ownership

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        sha = payload.get('sha')
        name = payload.get('name')
        email = payload.get('email')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(
            project, sha, name, email, **options
        )
        self.publish(payload, routing_key='measure')
