from fastapi import Request
from slowapi import Limiter


def get_client_ip(request: Request) -> str:
    if request.client is None:
        return "unknown"

    return request.client.host


def get_widget_key(request: Request) -> str:
    widget_id = request.path_params.get(
        "widget_id",
        "unknown"
    )

    return f"widget:{widget_id}"


limiter = Limiter(
    key_func=get_client_ip
)