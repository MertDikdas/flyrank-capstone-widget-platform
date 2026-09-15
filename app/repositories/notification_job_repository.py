from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification_job import NotificationJob


class NotificationJobRepository:

    @staticmethod
    def create(
        db: Session,
        job: NotificationJob
    ) -> NotificationJob:

        db.add(job)
        db.flush()

        return job

    @staticmethod
    def get_due_jobs(
        db: Session,
        now: datetime,
        limit: int = 20
    ) -> list[NotificationJob]:

        statement = (
            select(NotificationJob)
            .where(
                NotificationJob.status.in_([
                    "PENDING",
                    "RETRYING"
                ]),
                NotificationJob.next_attempt_at <= now
            )
            .order_by(
                NotificationJob.next_attempt_at.asc()
            )
            .limit(limit)
        )

        return list(
            db.scalars(statement).all()
        )