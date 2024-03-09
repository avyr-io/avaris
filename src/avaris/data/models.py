from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()


class SQLExecutionResult(Base):
    __tablename__ = 'execution_results'
    id = Column(String, primary_key=True)
    name = Column(String)
    task = Column(String)
    result = Column(JSON)
    timestamp = Column(DateTime)
