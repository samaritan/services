import logging

from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy

from .schemas import CommitSchema, LastModifierSchema, LineChangesSchema

METRIC = 'interactivechurn'
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


def _get_interactivechurn(project, commit, path, repository_rpc):
    linechanges = _get_linechanges(project, commit, path, repository_rpc)

    deletions = linechanges.linechanges[path]['-']
    if not deletions:
        return 0.0

    lastmodifiers = _get_lastmodifiers(
        project, commit, path, deletions, repository_rpc
    )
    nlines = (
        len(i.lines)
        for i in lastmodifiers if i.commit.author != commit.author
    )
    return sum(nlines) / len(deletions)


def _get_lastmodifiers(project, commit, path, lines, repository_rpc):
    commit = CommitSchema().dump(commit)
    lastmodifiers = repository_rpc.get_lastmodifiers(
        project, commit, path, lines
    )
    return LastModifierSchema(many=True).load(lastmodifiers)


def _get_linechanges(project, commit, path, repository_rpc):
    linechanges = repository_rpc.get_linechanges(project, commit.sha, path)
    return LineChangesSchema().load(linechanges)


class InteractiveChurnService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        commit = self._get_commit(project, sha)

        interactivechurn = _get_interactivechurn(
            project, commit, path, self.repository_rpc
        )
        return interactivechurn

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        sha = payload.get('sha')
        path = payload.get('path')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(project, sha, path, **options)
        self.publish(payload, routing_key='measure')

    def _get_commit(self, project, sha):
        commit = self.repository_rpc.get_commit(project, sha)
        return CommitSchema().load(commit)
