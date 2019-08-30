import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from . import utilities
from .hunk import get_hunks
from .schemas import HunkSchema, PatchSchema, ProjectSchema

logger = logging.getLogger(__name__)


class HunkService:
    name = 'hunk'

    config = Config()
    project_rpc = RpcProxy('project')
    repository_rpc = RpcProxy('repository')

    @rpc
    def collect(self, project, processes=os.cpu_count(), **options):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project))

        hunks = list()
        commits = self.repository_rpc.get_commits(project.name, processes)
        for chunk in utilities.chunk(commits, size=round(len(commits) * 0.05)):
            patches = self.repository_rpc.get_patches(project.name, chunk)
            patches = PatchSchema(many=True).load(patches)
            hunks.extend(get_hunks(patches))
            patches.clear()

        return HunkSchema(many=True).dump(hunks)
