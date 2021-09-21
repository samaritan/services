import logging

from kombu.messaging import Exchange, Queue
from nameko.dependency_providers import Config
from nameko.messaging import consume, Publisher
from nameko.rpc import rpc, RpcProxy
from sklearn.feature_extraction.text import CountVectorizer

METRIC = 'messagetokens'
exchange = Exchange(name='async.metrics')
logger = logging.getLogger(__name__)
queue = Queue(name=f'async-{METRIC}', routing_key=METRIC, exchange=exchange)


class MessageTokensService:
    name = METRIC

    config = Config()
    publish = Publisher(exchange=exchange)
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, **options):
        logger.debug(project)

        message = self.repository_rpc.get_message(project, sha)

        vectorizer = CountVectorizer(binary=True)
        vectorizer.fit([message])
        return vectorizer.get_feature_names()

    @consume(queue=queue)
    def handle_collect(self, payload):
        project = payload.get('project')
        sha = payload.get('sha')
        options = payload.get('options', dict())
        payload['measure'] = self.collect(project, sha, **options)
        self.publish(payload, routing_key='measure')
