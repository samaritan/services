import logging

from nameko_sqlalchemy import Database
from nameko.dependency_providers import Config
from nameko.rpc import rpc

from .exceptions import NotFound
from .models import Base, Project
from .schemas import ProjectSchema

logger = logging.getLogger(__name__)


class ProjectService:
    name = 'project'

    config = Config()
    database = Database(Base)

    @rpc
    def get(self, project):
        logger.debug(project)

        _project = None
        with self.database.get_session() as session:
            _project = session.query(Project) \
                              .filter_by(name=project) \
                              .one_or_none()
            if _project is None:
                raise NotFound('{} not found'.format(project))

        return ProjectSchema().dump(_project)
