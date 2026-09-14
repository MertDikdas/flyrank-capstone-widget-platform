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


router = APIRouter(
    prefix="/public",
    tags=["Public"]
)


@router.post(
    "/widgets/{widget_id}/submissions",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_submission(
    widget_id: uuid.UUID,
    data: SubmissionCreate,
    request: Request,
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