import uuid

from fastapi import (
    APIRouter,
    Depends,
    Header,
    Request,
    status,
    Response
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

from app.schemas.widget import PublicWidgetConfig
from app.services.widget_service import WidgetService

from fastapi.responses import FileResponse

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

@router.get(
    "/widgets/{widget_id}/config",
    response_model=PublicWidgetConfig
)
def get_public_widget_config(
    widget_id: uuid.UUID,
    response: Response,
    db: Session = Depends(get_db)
):
    response.headers[
        "Cache-Control"
    ] = "public, max-age=60"

    return WidgetService.get_public_config(
        db=db,
        widget_id=widget_id
    )

@router.get(
    "/../static/widget.v1.js",
    include_in_schema=False
)
def serve_widget_script():
    return FileResponse(
        path="widget/widget.v1.js",
        media_type="application/javascript",
        headers={
            "Cache-Control":
                "public, max-age=31536000, immutable"
        }
    )