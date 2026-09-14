from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.tenant import Tenant
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


class AuthService:

    @staticmethod
    def register(
        db: Session,
        data: RegisterRequest
    ) -> UserResponse:

        existing_user = UserRepository.get_by_email(
            db,
            data.email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        tenant = Tenant(
            name=data.tenant_name
        )

        user = User(
            tenant_id=tenant.id,
            email=data.email,
            password_hash=hash_password(data.password)
        )

        try:
            db.add(tenant)
            db.flush()

            user.tenant_id = tenant.id

            db.add(user)
            db.commit()
            db.refresh(user)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        return UserResponse.model_validate(user)

    @staticmethod
    def login(
        db: Session,
        data: LoginRequest
    ) -> TokenResponse:

        user = UserRepository.get_by_email(
            db,
            data.email
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not verify_password(
            data.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        access_token = create_access_token(
            subject=str(user.id)
        )

        return TokenResponse(
            access_token=access_token
        )