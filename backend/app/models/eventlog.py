
from sqlalchemy import Column, Integer, String
from database import Base
from event_log_cache import get_log_data


class Eventlog(Base):
    __tablename__ = "eventlogs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    path = Column(String)

    case_id = Column(String, nullable=True)
    timestamp = Column(String, nullable=True)
    activity = Column(String, nullable=True)

    column_count = Column(Integer)
    entry_count = Column(Integer)

    def log_data(self):
        return get_log_data(self)
