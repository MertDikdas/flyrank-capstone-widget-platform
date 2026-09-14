import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.widget import Widget
from app.repositories.widget_repository import WidgetRepository
from app.schemas.widget import (
    WidgetCreate,
    WidgetResponse,
    WidgetUpdate,
)


class WidgetService:

    @staticmethod
    def create(
        db: Session,
        current_user: User,
        data: WidgetCreate
    ) -> WidgetResponse:

        widget = Widget(
            tenant_id=current_user.tenant_id,
            name=data.name,
            type=data.type.value,
            title=data.title,
            description=data.description,
            button_text=data.button_text,
            fields=[
                field.model_dump()
                for field in data.fields
            ],
            display_options=data.display_options,
            is_active=True
        )

        WidgetRepository.create(
            db,
            widget
        )

        db.commit()
        db.refresh(widget)

        return WidgetResponse.model_validate(
            widget
        )

    @staticmethod
    def get_all(
        db: Session,
        current_user: User
    ) -> list[WidgetResponse]:

        widgets = WidgetRepository.get_all_by_tenant(
            db,
            current_user.tenant_id
        )

        return [
            WidgetResponse.model_validate(widget)
            for widget in widgets
        ]

    @staticmethod
    def get_by_id(
        db: Session,
        current_user: User,
        widget_id: uuid.UUID
    ) -> WidgetResponse:

        widget = WidgetRepository.get_by_id(
            db,
            widget_id,
            current_user.tenant_id
        )

        if widget is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )

        return WidgetResponse.model_validate(
            widget
        )

    @staticmethod
    def update(
        db: Session,
        current_user: User,
        widget_id: uuid.UUID,
        data: WidgetUpdate
    ) -> WidgetResponse:

        widget = WidgetRepository.get_by_id(
            db,
            widget_id,
            current_user.tenant_id
        )

        if widget is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )

        updates = data.model_dump(
            exclude_unset=True
        )

        if "type" in updates:
            updates["type"] = updates["type"].value

        if "fields" in updates:
            updates["fields"] = [
                field.model_dump()
                for field in data.fields
            ]

        for key, value in updates.items():
            setattr(
                widget,
                key,
                value
            )

        db.commit()
        db.refresh(widget)

        return WidgetResponse.model_validate(
            widget
        )

    @staticmethod
    def delete(
        db: Session,
        current_user: User,
        widget_id: uuid.UUID
    ) -> None:

        widget = WidgetRepository.get_by_id(
            db,
            widget_id,
            current_user.tenant_id
        )

        if widget is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )

        WidgetRepository.delete(
            db,
            widget
        )

        db.commit()