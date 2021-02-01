import logging
import math

from nameko_sqlalchemy import DatabaseSession
from nameko.dependency_providers import Config
from nameko.events import EventDispatcher
from nameko.rpc import rpc

from .exceptions import NotFound
from .models import Base, Project
from .schemas import ProjectSchema

PER_PAGE_DEFAULT = 30
logger = logging.getLogger(__name__)


class ProjectService:
    name = 'project'

    config = Config()
    database = DatabaseSession(Base)
    dispatch = EventDispatcher()

    @rpc
    def get(self, owner=None, repository=None, page=1,
            per_page=PER_PAGE_DEFAULT):
        if owner is not None and repository is not None:
            project = self.database.query(Project) \
                .filter_by(owner=owner, repository=repository) \
                .one_or_none()
            if project is None:
                raise NotFound(f'{owner}/{repository} not found')
            return ProjectSchema().dump(project)
        projects = self.database.query(Project)
        if owner is not None:
            projects = projects.filter_by(owner=owner)
        return ProjectSchema(many=True).dump(projects)

    @rpc
    def create(self, project):
        project = Project(**project)
        self.database.add(project)
        self.database.commit()
        project = ProjectSchema().dump(project)
        self.dispatch('project_created', {'project': project})
        return project

    def _paginate(self, query, page, per_page):
        count = query.count()
        first, last = 1, math.ceil(count / per_page)
        next_ = (page + 1) if page < last else None
        previous = (page - 1) if page > 1 else None
        data = query.limit(page).offset((page - 1) * per_page)
        return data
