import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.submission import Submission
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.widget_repository import WidgetRepository
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionResponse,
)


class SubmissionService:

    @staticmethod
    def validate_payload(
        widget_fields: list,
        payload: dict
    ) -> None:

        allowed_fields = {
            field["name"]
            for field in widget_fields
        }

        required_fields = {
            field["name"]
            for field in widget_fields
            if field.get("required", False)
        }

        received_fields = set(payload.keys())

        missing_fields = (
            required_fields - received_fields
        )

        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "message": "Missing required fields",
                    "fields": sorted(missing_fields)
                }
            )

        unknown_fields = (
            received_fields - allowed_fields
        )

        if unknown_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "message": "Unknown fields",
                    "fields": sorted(unknown_fields)
                }
            )

        for key, value in payload.items():

            if not isinstance(value, str):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"Field '{key}' must be a string"
                )

            if len(value) > 5000:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=f"Field '{key}' is too large"
                )

    @staticmethod
    def create(
        db: Session,
        widget_id: uuid.UUID,
        data: SubmissionCreate,
        idempotency_key: str,
        ip_address: str | None
    ) -> SubmissionResponse:

        widget = WidgetRepository.get_public_by_id(
            db,
            widget_id
        )

        if widget is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Widget not found"
            )

        existing = (
            SubmissionRepository.get_by_idempotency_key(
                db,
                widget_id,
                idempotency_key
            )
        )

        if existing is not None:
            return SubmissionResponse.model_validate(
                existing
            )

        SubmissionService.validate_payload(
            widget.fields,
            data.payload
        )

        submission = Submission(
            tenant_id=widget.tenant_id,
            widget_id=widget.id,
            payload=data.payload,
            idempotency_key=idempotency_key,
            ip_address=ip_address
        )

        try:
            SubmissionRepository.create(
                db,
                submission
            )

            db.commit()
            db.refresh(submission)

        except IntegrityError:
            db.rollback()

            existing = (
                SubmissionRepository.get_by_idempotency_key(
                    db,
                    widget_id,
                    idempotency_key
                )
            )

            if existing is None:
                raise

            return SubmissionResponse.model_validate(
                existing
            )

        return SubmissionResponse.model_validate(
            submission
        )