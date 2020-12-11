from marshmallow import Schema, fields, post_load

from ..models import Metric, ProjectMetric


class MetricSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    granularity = fields.String()
    service = fields.String()

    @post_load
    def make_metric(self, data, **kwargs):
        return Metric(**data)


class ProjectMetricSchema(Schema):
    metric_id = fields.Integer()
    project_id = fields.Integer()
    enabled = fields.Boolean()

    @post_load
    def make_projectmetric(self, data, **kwargs):
        return ProjectMetric(**data)
