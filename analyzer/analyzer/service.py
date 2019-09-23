import logging
import os
import tempfile

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .analyzer import analyze
from .codedx import CodeDx
from .exceptions import NotCloned
from .repository import Repository
from .schemas import ProjectSchema

logger = logging.getLogger(__name__)


class AnalyzerService:
    name = 'analyzer'

    config = Config()
    codedx = CodeDx()
    project_rpc = RpcProxy('project')

    @rpc
    def analyze(self, project, sha):
        logger.debug(project)

        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        return self._analyze(project, sha, repository)

    def _analyze(self, project, sha, repository):
        job = None
        with tempfile.TemporaryDirectory() as path:
            archive = repository.archive(sha, path)
            if archive is None:
                raise Exception(f'Failed to archive {project.name}@{sha}')

            name = f'{project.name}_{sha}'
            job = analyze(name, archive, self.codedx)
        return job

    def _get_repository(self, project):
        path = os.path.join(self.config['REPOSITORIES_ROOT'], project.name)
        if not os.path.exists(path):
            raise NotCloned('{} has not been cloned yet'.format(project.name))
        repository = Repository(path)
        return repository
