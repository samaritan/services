import logging

from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy

from .schemas import CommitSchema

METRIC = 'pastauthors'
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


class PastAuthorsService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        commits = self.repository_rpc.get_commits(project, sha, path)
        commits = CommitSchema(many=True).load(commits)

        commit = self.repository_rpc.get_commit(project, sha)
        commit = CommitSchema().load(commit)

        return len({c.author for c in commits} - {commit.author})

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        sha = payload.get('sha')
        path = payload.get('path')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(project, sha, path, **options)
        self.publish(payload, routing_key='measure')
