from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.widgets import router as widgets_router
from app.api.public import router as public_router
from app.api.static import router as static_router
from app.core.database import check_database_connection

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from contextlib import asynccontextmanager

from app.core.rate_limit import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()

    yield

    stop_scheduler()

app = FastAPI(
    title="Embeddable Widget & Lead-Capture Platform",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Idempotency-Key",
    ],
)

from app.core.scheduler import (
    start_scheduler,
    stop_scheduler,
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

app.add_middleware(
    SlowAPIMiddleware
)

app.include_router(auth_router)
app.include_router(widgets_router)
app.include_router(public_router)
app.include_router(static_router)

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/health/db")
def database_health():
    try:
        check_database_connection()

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )