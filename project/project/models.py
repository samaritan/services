from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class Project(DeclarativeBase):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    owner = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    language = Column(Text, nullable=False)
    repository_url = Column(Text, nullable=False)

    def __str__(self):
        return self.name
