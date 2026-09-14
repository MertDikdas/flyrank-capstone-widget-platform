import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SubmissionCreate(BaseModel):
    payload: dict[str, Any] = Field(
        min_length=1
    )


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    widget_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )