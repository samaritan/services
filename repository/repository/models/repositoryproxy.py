import logging

from zope.interface.declarations import implementer

from . import irepository
from ..schemas import ChangesSchema, CommitSchema, DeveloperSchema, \
                      FileSchema, ModuleSchema, MovesSchema

logger = logging.getLogger(__name__)


@implementer(irepository.IRepository)
class RepositoryProxy:
    def __init__(self, project, cache, repository):
        self._project = project
        self._cache = cache
        self._repository = repository

    def get_changes(self):
        item = 'changes'
        schema = ChangesSchema()

        for value in self._get(item, schema, self._repository.get_changes):
            yield value

    def get_commits(self):
        item = 'commits'
        schema = CommitSchema()

        for value in self._get(item, schema, self._repository.get_commits):
            yield value

    def get_developers(self):
        item = 'developers'
        schema = DeveloperSchema()

        for value in self._get(item, schema, self._repository.get_developers):
            yield value

    def get_files(self):
        item = 'files'
        schema = FileSchema()

        for value in self._get(item, schema, self._repository.get_files):
            yield value

    def get_modules(self):
        item = 'modules'
        schema = ModuleSchema()

        for value in self._get(item, schema, self._repository.get_modules):
            yield value

    def get_moves(self):
        item = 'moves'
        schema = MovesSchema()

        for value in self._get(item, schema, self._repository.get_moves):
            yield value

    def get_patches(self, commits):
        return self._repository.get_patches(commits)

    def get_path(self):
        return self._repository.get_path()

    def get_version(self):
        return self._repository.get_version()

    def _get(self, item, schema, getter):
        key = self._get_key(item)
        if key in self._cache:
            logger.debug('%s for %s in cache', item, self._project.name)
            for value in self._cache.get(key):
                yield schema.load(value).data
        else:
            logger.debug('%s for %s not in cache', item, self._project.name)
            valuelist = list()
            for value in getter():
                yield value
                valuelist.append(value)
            self._cache.set(key, schema.dump(valuelist, many=True).data)

    def _get_key(self, item):
        return f'{self._project.name}_{self._repository.get_version()}_{item}'
