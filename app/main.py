from fastapi import FastAPI, HTTPException

from app.api.auth import router as auth_router
from app.api.widgets import router as widgets_router
from app.api.public import router as public_router
from app.core.database import check_database_connection


app = FastAPI(
    title="Embeddable Widget & Lead-Capture Platform",
    version="0.1.0"
)


app.include_router(auth_router)
app.include_router(widgets_router)
app.include_router(public_router)

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