import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification_job import NotificationJob
from app.repositories.notification_job_repository import (
    NotificationJobRepository,
)


logger = logging.getLogger(__name__)


class NotificationService:

    @staticmethod
    def enqueue(
        db: Session,
        submission_id
    ) -> None:

        if not settings.notification_enabled:
            return

        job = NotificationJob(
            submission_id=submission_id,
            status="PENDING"
        )

        NotificationJobRepository.create(
            db,
            job
        )

        db.commit()

    @staticmethod
    def send_notification(
        job: NotificationJob
    ) -> None:

        if settings.notification_force_fail:
            raise RuntimeError(
                "Simulated notification failure"
            )

        print(
            f"[notification] submission={job.submission_id}"
        )

    @staticmethod
    def process_due_jobs(
        db: Session
    ) -> None:

        now = datetime.now(timezone.utc)

        jobs = NotificationJobRepository.get_due_jobs(
            db,
            now
        )

        for job in jobs:

            try:
                NotificationService.send_notification(
                    job
                )

                job.status = "COMPLETED"
                job.completed_at = datetime.now(
                    timezone.utc
                )
                job.last_error = None

            except Exception as exc:

                job.attempt_count += 1
                job.last_error = str(exc)

                if (
                    job.attempt_count
                    >= settings.notification_max_retries
                ):
                    job.status = "FAILED"

                    logger.error(
                        "Notification job permanently failed: "
                        "job_id=%s submission_id=%s error=%s",
                        job.id,
                        job.submission_id,
                        exc
                    )

                else:
                    job.status = "RETRYING"

                    job.next_attempt_at = (
                        datetime.now(timezone.utc)
                        + timedelta(
                            seconds=settings.notification_retry_seconds
                        )
                    )

            db.commit()