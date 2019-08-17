import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from . import utilities
from .patchtokens import get_patchtokens
from .schemas import PatchSchema, PatchTokensSchema, ProjectSchema

logger = logging.getLogger(__name__)

class PatchTokensService:
    name = 'patchtokens'

    config = Config()
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project)).data

        patches = list()
        commits = self.repository_rpc.get_commits(project.name, processes)
        for chunk in utilities.chunk(commits, size=round(len(commits) * 0.05)):
            _patches = self.repository_rpc.get_patches(project.name, chunk)
            patches.extend(_patches)
        patches = PatchSchema(many=True).load(patches).data
        patchtokens = get_patchtokens(patches)
        return PatchTokensSchema().dump(patchtokens).data
