import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class DashboardSubmissionResponse(BaseModel):
    id: uuid.UUID
    widget_id: uuid.UUID
    payload: dict[str, Any]
    country: str | None
    city: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class WidgetStat(BaseModel):
    widget_id: uuid.UUID
    widget_name: str
    count: int


class CountryStat(BaseModel):
    country: str
    count: int


class DailyStat(BaseModel):
    day: date
    count: int


class DashboardStatsResponse(BaseModel):
    total_submissions: int
    last_7_days: int
    per_widget: list[WidgetStat]
    countries: list[CountryStat]
    daily: list[DailyStat]