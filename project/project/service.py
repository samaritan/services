import logging

from nameko_sqlalchemy import DatabaseSession
from nameko.dependency_providers import Config
from nameko.rpc import rpc

from .exceptions import NotFound
from .models import Base, Project
from .schemas import ProjectSchema

logger = logging.getLogger(__name__)


class ProjectService:
    name = 'project'

    config = Config()
    database = DatabaseSession(Base)

    @rpc
    def get(self, project):
        logger.debug(project)

        _project = self.database.query(Project) \
            .filter_by(repository=project) \
            .one_or_none()
        if _project is None:
            raise NotFound('{} not found'.format(project))

        return ProjectSchema().dump(_project)
