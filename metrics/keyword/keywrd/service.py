import logging

from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy

from .exceptions import LanguageNotSupported
from .keywrd import Keywrd
from .schemas import ProjectSchema

METRIC = 'keyword'
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


class KeywordService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        project = ProjectSchema().load(project)
        if project.language.lower() not in self.config['KEYWORDS']:
            raise LanguageNotSupported(f'{project.language} not supported')
        keywords = self.config['KEYWORDS'].get(project.language.lower())
        keywrd = Keywrd(keywords=keywords)

        project = ProjectSchema().dump(project)
        patch = self.repository_rpc.get_patch(project, sha, path)
        return keywrd.get(patch)

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        sha = payload.get('sha')
        path = payload.get('path')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(project, sha, path, **options)
        self.publish(payload, routing_key='measure')
