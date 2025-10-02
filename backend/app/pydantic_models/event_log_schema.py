from pydantic import BaseModel


class EventLogColumnRequest(BaseModel):
    case_id: str
    activity: str
    timestamp: str
