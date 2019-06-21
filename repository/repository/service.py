import logging
import os

from diskcache import Cache
from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .exceptions import NotCloned
from .models import Repository, RepositoryProxy
from .schemas import ChangesSchema, CommitSchema, DeveloperSchema,       \
                     FileSchema, ModuleSchema, MovesSchema, PatchSchema, \
                     ProjectSchema

logger = logging.getLogger(__name__)


class RepositoryService:
    name = 'repository'

    config = Config()
    project_rpc = RpcProxy('project')

    @rpc
    def get_changes(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        changes = list(repository.get_changes())
        return ChangesSchema(many=True).dump(changes).data

    @rpc
    def get_commits(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        commits = list(repository.get_commits())
        return CommitSchema(many=True).dump(commits).data

    @rpc
    def get_developers(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        developers = list(repository.get_developers())
        return DeveloperSchema(many=True).dump(developers).data

    @rpc
    def get_files(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        files = list(repository.get_files())
        return FileSchema(many=True).dump(files).data

    @rpc
    def get_modules(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        modules = list(repository.get_modules())
        return ModuleSchema(many=True).dump(modules).data

    @rpc
    def get_moves(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        moves = list(repository.get_moves())
        return MovesSchema(many=True).dump(moves).data

    @rpc
    def get_patches(self, project, commits, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        commits = CommitSchema(many=True).load(commits).data
        repository = self._get_repository(project, processes)
        patches = list(repository.get_patches(commits))
        return PatchSchema(many=True).dump(patches).data

    @rpc
    def get_path(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        return repository.get_path()

    @rpc
    def get_version(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project)).data
        repository = self._get_repository(project, processes)
        return repository.get_version()

    def _get_path(self, project):
        return os.path.join(self.config['REPOSITORIES_ROOT'], project.name)

    def _get_repository(self, project, processes):
        path = self._get_path(project)
        if not os.path.exists(path):
            raise NotCloned('{} has not been cloned yet'.format(project.name))
        repository = Repository(path, processes)
        cache = Cache(self.config['CACHE_ROOT'])
        return RepositoryProxy(project, cache, repository)
