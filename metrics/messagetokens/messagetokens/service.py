import logging
import os

from eventlet.greenpool import GreenPool
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from . import utilities
from .messagetokens import get_messagetokens
from .schemas import MessageSchema, MessageTokensSchema, ProjectSchema

logger = logging.getLogger(__name__)


def _get_messages(project, commits, repository_rpc):
    return repository_rpc.get_messages(project.name, commits)


class MessageTokensService:
    name = 'messagetokens'

    config = Config()
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project))
        messages = self._get_messages(project)
        messagetokens = get_messagetokens(messages)
        return MessageTokensSchema().dump(messagetokens)

    def _get_messages(self, project):
        commits = self.repository_rpc.get_commits(project.name)
        chunks = utilities.chunk(commits, size=round(len(commits) * 0.05))

        pool = GreenPool(os.cpu_count())
        arguments = [(project, c, self.repository_rpc) for c in chunks]
        messages = list()
        for _messages in pool.starmap(_get_messages, arguments):
            messages.extend(_messages)
        return MessageSchema(many=True).load(messages)
