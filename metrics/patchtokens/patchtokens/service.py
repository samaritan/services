import logging

from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy
from sklearn.feature_extraction.text import CountVectorizer

METRIC = 'patchtokens'
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


class PatchTokensService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, path, **options):
        logger.debug(project)

        patch = self.repository_rpc.get_patch(project, sha, path)
        if patch:
            vectorizer = CountVectorizer(binary=True)
            vectorizer.fit([patch])
            return vectorizer.get_feature_names()
        return None if patch is None else list()

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        sha = payload.get('sha')
        path = payload.get('path')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(project, sha, path, **options)
        self.publish(payload, routing_key='measure')
