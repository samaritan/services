import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from . import utilities
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

        keyword = list()
        commits = self.repository_rpc.get_commits(project.name, processes)
        for chunk in utilities.chunk(commits, size=round(len(commits) * 0.05)):
            patches = self.repository_rpc.get_patches(project.name, chunk)
            patches = PatchSchema(many=True).load(patches).data
            keyword.extend(get_keywords(patches, keywords))
            patches.clear()

        return KeywordSchema(many=True).dump(keyword).data
