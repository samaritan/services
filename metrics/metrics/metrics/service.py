import logging

from nameko.events import EventDispatcher, event_handler
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

    @event_handler('project', 'project_created')
    def handle_project_created(self, payload):
        logger.debug('handle_project_created')
        project = ProjectSchema().load(payload.get('project'))
        metrics = self.database.query(Metric.id, Metric.enabled)
        for metric in metrics:
            project_metric = ProjectMetric(
                project_id=project.id, metric_id=metric.id,
                enabled=metric.enabled
            )
            self.database.add(project_metric)
        self.database.commit()
