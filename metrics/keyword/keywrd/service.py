import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .exceptions import LanguageNotSupported
from .keywrd import Keywrd
from .schemas import ProjectSchema

logger = logging.getLogger(__name__)


class KeywordService:
    name = 'keyword'

    config = Config()
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
