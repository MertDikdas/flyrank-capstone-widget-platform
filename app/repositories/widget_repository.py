import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.widget import Widget


class WidgetRepository:

    @staticmethod
    def create(
        db: Session,
        widget: Widget
    ) -> Widget:

        db.add(widget)
        db.flush()

        return widget

    @staticmethod
    def get_by_id(
        db: Session,
        widget_id: uuid.UUID,
        tenant_id: uuid.UUID
    ) -> Widget | None:

        statement = select(Widget).where(
            Widget.id == widget_id,
            Widget.tenant_id == tenant_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_all_by_tenant(
        db: Session,
        tenant_id: uuid.UUID
    ) -> list[Widget]:

        statement = (
            select(Widget)
            .where(
                Widget.tenant_id == tenant_id
            )
            .order_by(
                Widget.created_at.desc()
            )
        )

        return list(
            db.scalars(statement).all()
        )

    @staticmethod
    def delete(
        db: Session,
        widget: Widget
    ) -> None:

        db.delete(widget)