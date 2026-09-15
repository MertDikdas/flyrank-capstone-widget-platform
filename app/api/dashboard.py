import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import (
    DashboardStatsResponse,
    DashboardSubmissionResponse,
)
from app.services.dashboard_service import (
    DashboardService,
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/submissions",
    response_model=list[DashboardSubmissionResponse]
)
def get_submissions(
    widget_id: uuid.UUID | None = None,
    country: str | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=100
    ),
    offset: int = Query(
        default=0,
        ge=0
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return DashboardService.get_submissions(
        db=db,
        current_user=current_user,
        widget_id=widget_id,
        country=country,
        limit=limit,
        offset=offset
    )


@router.get(
    "/submissions/{submission_id}",
    response_model=DashboardSubmissionResponse
)
def get_submission(
    submission_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return DashboardService.get_submission(
        db=db,
        current_user=current_user,
        submission_id=submission_id
    )


@router.get(
    "/stats",
    response_model=DashboardStatsResponse
)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return DashboardService.get_stats(
        db=db,
        current_user=current_user
    )