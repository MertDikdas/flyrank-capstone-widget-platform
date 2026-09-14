import uuid

from fastapi import (
    APIRouter,
    Depends,
    Header,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionResponse,
)
from app.services.submission_service import SubmissionService

from app.core.rate_limit import (
    get_widget_key,
    limiter,
)

router = APIRouter(
    prefix="/public",
    tags=["Public"]
)


@router.post(
    "/widgets/{widget_id}/submissions",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
@limiter.limit(
    "20/minute",
    key_func=get_widget_key
)
def create_submission(
    request: Request,
    widget_id: uuid.UUID,
    data: SubmissionCreate,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        max_length=100
    ),
    db: Session = Depends(get_db)
):
    ip_address = (
        request.client.host
        if request.client
        else None
    )

    return SubmissionService.create(
        db=db,
        widget_id=widget_id,
        data=data,
        idempotency_key=idempotency_key,
        ip_address=ip_address
    )