from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(
    prefix="/static",
    tags=["Static"]
)


@router.get(
    "/widget.v1.js",
    include_in_schema=False
)
def serve_widget_script():
    return FileResponse(
        path="widget/widget.v1.js",
        media_type="application/javascript",
        headers={
            "Cache-Control":
                "public, max-age=31536000, immutable"
        }
    )