import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.submission import Submission
from app.models.widget import Widget


class DashboardRepository:

    @staticmethod
    def get_submissions(
        db: Session,
        tenant_id: uuid.UUID,
        widget_id: uuid.UUID | None = None,
        country: str | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Submission]:

        statement = select(Submission).where(
            Submission.tenant_id == tenant_id
        )

        if widget_id is not None:
            statement = statement.where(
                Submission.widget_id == widget_id
            )

        if country is not None:
            statement = statement.where(
                Submission.country == country
            )

        statement = (
            statement
            .order_by(
                Submission.created_at.desc()
            )
            .limit(limit)
            .offset(offset)
        )

        return list(
            db.scalars(statement).all()
        )

    @staticmethod
    def get_submission_by_id(
        db: Session,
        tenant_id: uuid.UUID,
        submission_id: uuid.UUID
    ) -> Submission | None:

        statement = select(Submission).where(
            Submission.id == submission_id,
            Submission.tenant_id == tenant_id
        )

        return db.scalar(statement)

    @staticmethod
    def get_total_count(
        db: Session,
        tenant_id: uuid.UUID
    ) -> int:

        statement = select(
            func.count(Submission.id)
        ).where(
            Submission.tenant_id == tenant_id
        )

        return db.scalar(statement) or 0

    @staticmethod
    def get_last_7_days_count(
        db: Session,
        tenant_id: uuid.UUID
    ) -> int:

        since = (
            datetime.now(timezone.utc)
            - timedelta(days=7)
        )

        statement = select(
            func.count(Submission.id)
        ).where(
            Submission.tenant_id == tenant_id,
            Submission.created_at >= since
        )

        return db.scalar(statement) or 0

    @staticmethod
    def get_per_widget_stats(
        db: Session,
        tenant_id: uuid.UUID
    ):
        statement = (
            select(
                Widget.id,
                Widget.name,
                func.count(Submission.id)
            )
            .join(
                Submission,
                Submission.widget_id == Widget.id
            )
            .where(
                Submission.tenant_id == tenant_id
            )
            .group_by(
                Widget.id,
                Widget.name
            )
            .order_by(
                func.count(Submission.id).desc()
            )
        )

        return db.execute(statement).all()

    @staticmethod
    def get_country_stats(
        db: Session,
        tenant_id: uuid.UUID
    ):
        statement = (
            select(
                Submission.country,
                func.count(Submission.id)
            )
            .where(
                Submission.tenant_id == tenant_id,
                Submission.country.is_not(None)
            )
            .group_by(
                Submission.country
            )
            .order_by(
                func.count(Submission.id).desc()
            )
        )

        return db.execute(statement).all()

    @staticmethod
    def get_daily_stats(
        db: Session,
        tenant_id: uuid.UUID
    ):
        since = (
            datetime.now(timezone.utc)
            - timedelta(days=7)
        )

        day = func.date(
            Submission.created_at
        )

        statement = (
            select(
                day,
                func.count(Submission.id)
            )
            .where(
                Submission.tenant_id == tenant_id,
                Submission.created_at >= since
            )
            .group_by(day)
            .order_by(day)
        )

        return db.execute(statement).all()