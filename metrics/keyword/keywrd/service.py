import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .exceptions import LanguageNotSupported
from .keywrd import get_keywords
from .schemas import KeywordSchema, PatchSchema, ProjectSchema

logger = logging.getLogger(__name__)


class KeywordService:
    name = 'keyword'

    config = Config()
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project)).data
        if project.language.lower() not in self.config['KEYWORDS']:
            raise LanguageNotSupported(f'{project.language} not supported')
        keywords = self.config['KEYWORDS'].get(project.language.lower())

        patches = self.repository_rpc.get_patches(project.name, processes)
        patches = PatchSchema(many=True).load(patches).data

        keywords = get_keywords(patches, keywords)
        return KeywordSchema(many=True).dump(keywords).data
