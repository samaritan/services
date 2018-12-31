import logging

from zope.interface.declarations import implementer

from . import irepository
from ..schemas import ChangesSchema, CommitSchema, DeveloperSchema, \
                      FileSchema, ModuleSchema

logger = logging.getLogger(__name__)


@implementer(irepository.IRepository)
class RepositoryProxy:
    def __init__(self, project, redis, repository):
        self._project = project
        self._redis = redis
        self._repository = repository

    def get_changes(self):
        item = 'changes'

        changes = self._lookup(item)
        if changes is None:
            changes = self._repository.get_changes()
            self._cache(item, ChangesSchema(many=True).dumps(changes).data)
        else:
            changes = ChangesSchema(many=True).loads(changes).data

        return ChangesSchema(many=True).dump(changes).data

    def get_commits(self):
        item = 'commits'

        commits = self._lookup(item)
        if commits is None:
            commits = self._repository.get_commits()
            self._cache(item, CommitSchema(many=True).dumps(commits).data)
        else:
            commits = CommitSchema(many=True).loads(commits).data

        return CommitSchema(many=True).dump(commits).data

    def get_developers(self):
        item = 'developers'

        developers = self._lookup(item)
        if developers is None:
            developers = self._repository.get_developers()
            self._cache(
                item, DeveloperSchema(many=True).dumps(developers).data
            )
        else:
            developers = DeveloperSchema(many=True).loads(developers).data

        return DeveloperSchema(many=True).dump(developers).data

    def get_files(self):
        item = 'files'

        files = self._lookup(item)
        if files is None:
            files = self._repository.get_files()
            self._cache(item, FileSchema(many=True).dumps(files).data)
        else:
            files = FileSchema(many=True).loads(files).data

        return FileSchema(many=True).dump(files).data

    def get_modules(self):
        item = 'modules'

        modules = self._lookup(item)
        if modules is None:
            modules = self._repository.get_modules()
            self._cache(item, ModuleSchema(many=True).dumps(modules).data)
        else:
            modules = ModuleSchema(many=True).loads(modules).data

        return ModuleSchema(many=True).dump(modules).data

    def get_path(self):
        return self._repository.get_path()

    def _cache(self, item, value):
        self._redis.set('{}_{}'.format(self._project.name, item), value)

    def _lookup(self, item):
        value = self._redis.get('{}_{}'.format(self._project.name, item))
        if value is not None:
            logger.debug('%s for %s in cache', item, self._project.name)
        else:
            logger.debug('%s for %s not in cache', item, self._project.name)
        return value
