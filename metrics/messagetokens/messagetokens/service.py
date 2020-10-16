import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .messagetokens import get_messagetokens
from .schemas import MessageSchema, MessageTokensSchema

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
        messagetokens = get_messagetokens(message)

        return MessageTokensSchema().dump(messagetokens)
