import logging

from eventlet.greenpool import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .messagetokens import get_messagetokens
from .schemas import CommitSchema, MessageSchema, MessageTokensSchema

logger = logging.getLogger(__name__)


def _get_message(project, commit, repository_rpc):
    return repository_rpc.get_message(project, commit.sha)


class MessageTokensService:
    name = 'messagetokens'

    config = Config()
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, sha, **options):
        logger.debug(project)

        messages = self._get_messages(project, sha)
        messagetokens = get_messagetokens(messages)
        return MessageTokensSchema().dump(messagetokens)

    def _get_messages(self, project, sha):
        commits = [self.repository_rpc.get_commit(project, sha)]
        commits = CommitSchema(many=True).load(commits)

        pool = GreenPool()
        arguments = ((project, c, self.repository_rpc) for c in commits)
        messages = list()
        for item in pool.starmap(_get_message, arguments):
            messages.append(item)
        return MessageSchema(many=True).load(messages)
