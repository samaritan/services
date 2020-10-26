import logging
import os

from nameko.dependency_providers import Config
from nameko.rpc import rpc, RpcProxy

from .exceptions import NotCloned
from .redis import Redis
from .repository import Repository
from .runner import Runner
from .schemas import ChangeSchema, ChangesSchema, CommitSchema,            \
                     DeltaSchema, DeltasSchema, DeveloperSchema,           \
                     FileSchema, LastModifierSchema, LineChangesSchema,    \
                     MessageSchema, ModuleSchema, MoveSchema, MovesSchema, \
                     PatchSchema, ProjectSchema

logger = logging.getLogger(__name__)


class RepositoryService:
    name = 'repository'

    config = Config()
    redis = Redis()
    project_rpc = RpcProxy('project')

    @rpc
    def get_changes(self, project, sha, path=None):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        changes = list(repository.get_changes(sha, path))
        return ChangesSchema(many=True).dump(changes)

    @rpc
    def get_commit(self, project, sha):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        commit = repository.get_commit(sha)
        return CommitSchema().dump(commit)

    @rpc
    def get_commits(self, project, sha=None, path=None):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        commits = list(repository.get_commits(sha, path))
        return CommitSchema(many=True).dump(commits)

    @rpc
    def get_content(self, project, oid):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)

        key = f'{project.name}_{oid}'
        content = self.redis.get(key)
        if content is None:
            content = repository.get_content(oid)
            if content is not None:
                self.redis.set(key, content)
        else:
            content = content.decode(errors='replace')
        return content

    @rpc
    def get_deltas(self, project, sha, path):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        deltas = repository.get_deltas(sha, path)
        return DeltasSchema().dump(deltas)

    @rpc
    def get_developers(self, project):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        developers = list(repository.get_developers())
        return DeveloperSchema(many=True).dump(developers)

    @rpc
    def get_files(self, project):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        files = list(repository.get_files())
        return FileSchema(many=True).dump(files)

    @rpc
    def get_lastmodifiers(self, project, commit, path, lines):
        project = ProjectSchema().load(self.project_rpc.get(project))
        commit = CommitSchema().load(commit)
        repository = self._get_repository(project)
        lastmodifiers = list(repository.get_lastmodifiers(commit, path, lines))
        return LastModifierSchema(many=True).dump(lastmodifiers)

    @rpc
    def get_linechanges(self, project, sha, path=None):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        linechanges = repository.get_linechanges(sha, path)
        return LineChangesSchema().dump(linechanges)

    @rpc
    def get_message(self, project, sha):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        message = repository.get_message(sha)
        return MessageSchema().dump(message)

    @rpc
    def get_modules(self, project):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        modules = list(repository.get_modules())
        return ModuleSchema(many=True).dump(modules)

    @rpc
    def get_moves(self, project, similarity=100):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        moves = list(repository.get_moves(similarity))
        return MovesSchema(many=True).dump(moves)

    @rpc
    def get_patch(self, project, sha, path):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        patch = repository.get_patch(sha, path)
        return PatchSchema().dump(patch)

    @rpc
    def get_path(self, project):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        return repository.get_path()

    @rpc
    def get_size(self, project, oid):
        content = self.get_content(project, oid)
        if content is not None:
            content = content.split('\n')
            return len(content) if content[-1] else len(content) - 1
        return None

    @rpc
    def get_version(self, project):
        project = ProjectSchema().load(self.project_rpc.get(project))
        repository = self._get_repository(project)
        return repository.get_version()

    def _get_path(self, project):
        return os.path.join(self.config['REPOSITORIES_ROOT'], project.name)

    def _get_repository(self, project):
        path = self._get_path(project)
        if not os.path.exists(path):
            raise NotCloned('{} has not been cloned yet'.format(project.name))
        runner = Runner(path)
        repository = Repository(path, project, runner)
        return repository
