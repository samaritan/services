from sqlalchemy import Column, Text
from sqlalchemy.ext.declarative import declarative_base

__all__ = ['Project']

DeclarativeBase = declarative_base()


class Project(DeclarativeBase):
    __tablename__ = 'project'

    name = Column(Text, primary_key=True)
    description = Column(Text, nullable=False)
    domain = Column(Text, nullable=False)
    language = Column(Text, nullable=False)
    project_url = Column(Text, nullable=False)
    repository_url = Column(Text, nullable=False)

    def __str__(self):
        return self.name
