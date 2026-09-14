import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.submission import Submission


class SubmissionRepository:

    @staticmethod
    def create(
        db: Session,
        submission: Submission
    ) -> Submission:

        db.add(submission)
        db.flush()

        return submission

    @staticmethod
    def get_by_idempotency_key(
        db: Session,
        widget_id: uuid.UUID,
        idempotency_key: str
    ) -> Submission | None:

        statement = select(Submission).where(
            Submission.widget_id == widget_id,
            Submission.idempotency_key == idempotency_key
        )

        return db.scalar(statement)