from pydantic import BaseModel, Field
from typing import Dict, Any


class Event(BaseModel):
    """
    Schema required for the event
    """

    tenant_id: str = Field(..., description="Tenant identifier")
    event_type: str = Field(..., description="Type of event: click, view, error, session_start, session_end")
    timestamp: float = Field(..., description="Unix timestamp of the event")
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the event"
    )
