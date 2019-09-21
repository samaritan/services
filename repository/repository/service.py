import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .cache import Cache
from .exceptions import NotCloned
from .repository import Repository
from .runner import Runner
from .schemas import ChangesSchema, CommitSchema, DeltasSchema,               \
                     DeveloperSchema, FileSchema, LineChangesSchema,          \
                     MessageSchema, ModuleSchema, MovesSchema, PatchSchema,   \
                     ProjectSchema

logger = logging.getLogger(__name__)


class RepositoryService:
    name = 'repository'

    cache = Cache()
    config = Config()
    project_rpc = RpcProxy('project')

    @rpc
    def get_changes(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project, processes)
        changes = list(repository.get_changes())
        return ChangesSchema(many=True).dump(changes)

    @rpc
    def get_commits(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project, processes)
        commits = list(repository.get_commits())
        return CommitSchema(many=True).dump(commits)

    @rpc
    def get_content(self, project, oid, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project, processes)
        return repository.get_content(oid)

    @rpc
    def get_deltas(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project, processes)
        developers = list(repository.get_deltas())
        return DeltasSchema(many=True).dump(developers)

    @rpc
    def get_developers(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project, processes)
        developers = list(repository.get_developers())
        return DeveloperSchema(many=True).dump(developers)

    @rpc
    def get_files(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project, processes)
        files = list(repository.get_files())
        return FileSchema(many=True).dump(files)

    @rpc
    def get_linechanges(self, project, commit, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        commit = CommitSchema().load(commit)
        repository = self._get_repository(project, processes)
        linechanges = repository.get_linechanges(commit)
        return LineChangesSchema().dump(linechanges)

    @rpc
    def get_messages(self, project, commits, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        commits = CommitSchema(many=True).load(commits)
        repository = self._get_repository(project, processes)
        messages = list(repository.get_messages(commits))
        return MessageSchema(many=True).dump(messages)

    @rpc
    def get_modules(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project, processes)
        modules = list(repository.get_modules())
        return ModuleSchema(many=True).dump(modules)

    @rpc
    def get_moves(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project, processes)
        moves = list(repository.get_moves())
        return MovesSchema(many=True).dump(moves)

    @rpc
    def get_patches(self, project, commits, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        commits = CommitSchema(many=True).load(commits)
        repository = self._get_repository(project, processes)
        patches = list(repository.get_patches(commits))
        return PatchSchema(many=True).dump(patches)

    @rpc
    def get_path(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project, processes)
        return repository.get_path()

    @rpc
    def get_version(self, project, processes=os.cpu_count()):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project, processes)
        return repository.get_version()

    def _get_path(self, project):
        return os.path.join(self.config['REPOSITORIES_ROOT'], project.name)

    def _get_repository(self, project, processes):
        path = self._get_path(project)
        if not os.path.exists(path):
            raise NotCloned('{} has not been cloned yet'.format(project.name))
        runner = Runner(path, self.cache)
        repository = Repository(path, project, runner)
        return repository
