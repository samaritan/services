import logging

from zope.interface.declarations import implementer

from . import irepository
from ..schemas import ChangesSchema, CommitSchema, DeveloperSchema, \
                      FileSchema, ModuleSchema

logger = logging.getLogger(__name__)


@implementer(irepository.IRepository)
class RepositoryProxy:
    def __init__(self, project, cache, repository):
        self._project = project
        self._cache = cache
        self._repository = repository

    def get_changes(self):
        item = 'changes'
        schema = ChangesSchema(many=True)

        changes = self._cache_get(item, schema)
        if changes is None:
            changes = self._repository.get_changes()
            self._cache_set(item, changes, schema)
        return changes

    def get_commits(self):
        item = 'commits'
        schema = CommitSchema(many=True)

        commits = self._cache_get(item, schema)
        if commits is None:
            commits = self._repository.get_commits()
            self._cache_set(item, commits, schema)
        return commits

    def get_developers(self):
        item = 'developers'
        schema = DeveloperSchema(many=True)

        developers = self._cache_get(item, schema)
        if developers is None:
            developers = self._repository.get_developers()
            self._cache_set(item, developers, schema)
        return developers

    def get_files(self):
        item = 'files'
        schema = FileSchema(many=True)

        files = self._cache_get(item, schema)
        if files is None:
            files = self._repository.get_files()
            self._cache_set(item, files, schema)
        return files

    def get_modules(self):
        item = 'modules'
        schema = ModuleSchema(many=True)

        modules = self._cache_get(item, schema)
        if modules is None:
            modules = self._repository.get_modules()
            self._cache_set(item, modules, schema)
        return modules

    def get_patches(self, commits):
        return self._repository.get_patches(commits)

    def get_path(self):
        return self._repository.get_path()

    def get_version(self):
        return self._repository.get_version()

    def _cache_get(self, item, schema):
        value = self._cache.get(self._get_key(item))
        if value is not None:
            logger.debug('%s for %s in cache', item, self._project.name)
            value = schema.load(value).data
        else:
            logger.debug('%s for %s not in cache', item, self._project.name)
        return value

    def _get_key(self, item):
        return f'{self._project.name}_{self._repository.get_version()}_{item}'

    def _cache_set(self, item, value, schema):
        self._cache.set(self._get_key(item), schema.dump(value).data)
