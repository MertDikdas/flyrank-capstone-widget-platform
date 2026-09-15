import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.dashboard_repository import (
    DashboardRepository,
)
from app.schemas.dashboard import (
    CountryStat,
    DailyStat,
    DashboardStatsResponse,
    DashboardSubmissionResponse,
    WidgetStat,
)


class DashboardService:

    @staticmethod
    def get_submissions(
        db: Session,
        current_user: User,
        widget_id: uuid.UUID | None,
        country: str | None,
        limit: int,
        offset: int
    ) -> list[DashboardSubmissionResponse]:

        submissions = (
            DashboardRepository.get_submissions(
                db=db,
                tenant_id=current_user.tenant_id,
                widget_id=widget_id,
                country=country,
                limit=limit,
                offset=offset
            )
        )

        return [
            DashboardSubmissionResponse.model_validate(
                submission
            )
            for submission in submissions
        ]

    @staticmethod
    def get_submission(
        db: Session,
        current_user: User,
        submission_id: uuid.UUID
    ) -> DashboardSubmissionResponse:

        submission = (
            DashboardRepository.get_submission_by_id(
                db=db,
                tenant_id=current_user.tenant_id,
                submission_id=submission_id
            )
        )

        if submission is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Submission not found"
            )

        return DashboardSubmissionResponse.model_validate(
            submission
        )

    @staticmethod
    def get_stats(
        db: Session,
        current_user: User
    ) -> DashboardStatsResponse:

        tenant_id = current_user.tenant_id

        total = DashboardRepository.get_total_count(
            db,
            tenant_id
        )

        last_7_days = (
            DashboardRepository.get_last_7_days_count(
                db,
                tenant_id
            )
        )

        widget_rows = (
            DashboardRepository.get_per_widget_stats(
                db,
                tenant_id
            )
        )

        country_rows = (
            DashboardRepository.get_country_stats(
                db,
                tenant_id
            )
        )

        daily_rows = (
            DashboardRepository.get_daily_stats(
                db,
                tenant_id
            )
        )

        return DashboardStatsResponse(
            total_submissions=total,
            last_7_days=last_7_days,

            per_widget=[
                WidgetStat(
                    widget_id=row[0],
                    widget_name=row[1],
                    count=row[2]
                )
                for row in widget_rows
            ],

            countries=[
                CountryStat(
                    country=row[0],
                    count=row[1]
                )
                for row in country_rows
            ],

            daily=[
                DailyStat(
                    day=row[0],
                    count=row[1]
                )
                for row in daily_rows
            ]
        )