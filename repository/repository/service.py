import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .dependencies import Redis
from .exceptions import NotCloned
from .models import Repository, RepositoryProxy
from .schemas import ProjectSchema

logger = logging.getLogger(__name__)


class RepositoryService:
    name = 'repository'

    config = Config()
    redis = Redis()
    project_rpc = RpcProxy('project')

    @rpc
    def get_changes(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        return repository.get_changes()

    @rpc
    def get_commits(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        return repository.get_commits()

    @rpc
    def get_developers(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        return repository.get_developers()

    @rpc
    def get_files(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        return repository.get_files()

    @rpc
    def get_modules(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        return repository.get_modules()

    @rpc
    def get_path(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        return repository.get_path()

    def _get_path(self, project):
        return os.path.join(self.config['REPOSITORIES_ROOT'], project.name)

    def _get_repository(self, project, processes):
        path = self._get_path(project)
        if not os.path.exists(path):
            raise NotCloned('{} has not been cloned yet'.format(project.name))
        repository = Repository(path, processes)
        return RepositoryProxy(project, self.redis, repository)
