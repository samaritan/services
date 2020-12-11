import logging

from nameko.events import EventDispatcher
from nameko.dependency_providers import Config
from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession

from .models import Base, Metric, ProjectMetric
from .schemas import MetricSchema, ProjectSchema

logger = logging.getLogger(__name__)


class MetricsService:
    name = 'metrics'

    config = Config()
    database = DatabaseSession(Base)
    dispatch = EventDispatcher()

    @rpc
    def get(self, project, granularity):
        project = ProjectSchema().load(project)
        metrics = self.database.query(Metric) \
                               .filter_by(granularity=granularity) \
                               .join(ProjectMetric) \
                               .filter_by(project_id=project.id) \
                               .filter_by(enabled=True) \
                               .all()
        return MetricSchema(many=True).dump(metrics)
