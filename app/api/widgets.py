import uuid

from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.widget import (
    EmbedSnippetResponse,
    WidgetCreate,
    WidgetResponse,
    WidgetUpdate,
)
from app.services.widget_service import WidgetService


router = APIRouter(
    prefix="/api/widgets",
    tags=["Widgets"]
)


@router.post(
    "",
    response_model=WidgetResponse,
    status_code=status.HTTP_201_CREATED
)
def create_widget(
    data: WidgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return WidgetService.create(
        db=db,
        current_user=current_user,
        data=data
    )


@router.get(
    "",
    response_model=list[WidgetResponse]
)
def get_widgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return WidgetService.get_all(
        db=db,
        current_user=current_user
    )


@router.get(
    "/{widget_id}",
    response_model=WidgetResponse
)
def get_widget(
    widget_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return WidgetService.get_by_id(
        db=db,
        current_user=current_user,
        widget_id=widget_id
    )


@router.patch(
    "/{widget_id}",
    response_model=WidgetResponse
)
def update_widget(
    widget_id: uuid.UUID,
    data: WidgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return WidgetService.update(
        db=db,
        current_user=current_user,
        widget_id=widget_id,
        data=data
    )


@router.delete(
    "/{widget_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_widget(
    widget_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    WidgetService.delete(
        db=db,
        current_user=current_user,
        widget_id=widget_id
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


@router.get(
    "/{widget_id}/embed",
    response_model=EmbedSnippetResponse
)
def get_embed_snippet(
    widget_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return WidgetService.get_embed_snippet(
        db=db,
        current_user=current_user,
        widget_id=widget_id
    )