import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy
from sklearn.feature_extraction.text import CountVectorizer

from .schemas import MessageSchema

logger = logging.getLogger(__name__)


class MessageTokensService:
    name = 'messagetokens'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, **options):
        logger.debug(project)

        message = self.repository_rpc.get_message(project, sha)
        message = MessageSchema().load(message)

        vectorizer = CountVectorizer(binary=True)
        vectorizer.fit([message.message])
        return vectorizer.get_feature_names()
