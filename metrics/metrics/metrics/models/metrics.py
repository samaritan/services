from functools import partial

from sqlalchemy import Boolean, Column, ForeignKey, Integer, \
                       String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
NNColumn = partial(Column, nullable=False)  # Not Null Column


class Metric(Base):
    __tablename__ = 'metric'

    id = Column(Integer, primary_key=True)
    name = NNColumn(String(125))
    granularity = NNColumn(String(125))
    service = NNColumn(String(125))

    # Constraints
    __table_args__ = (UniqueConstraint('name', 'granularity'),)


class ProjectMetric(Base):
    __tablename__ = 'project_metric'

    id = Column(Integer, primary_key=True)
    project_id = NNColumn(Integer, index=True)
    enabled = Column(Boolean, default=False, server_default='0')

    # Foreign Key(s)
    metric_id = NNColumn(Integer, ForeignKey('metric.id'))

    # Constraints
    __table_args__ = (UniqueConstraint('project_id', 'metric_id'),)
