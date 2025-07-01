from    fastapi                 import Request, status
from    starlette.responses     import Response
from    loggers                 import root_logger
import  time
import  uuid

SENSITIVE_FIELDS = {"password", "token", "access_token", "refresh_token", "secret"}
MICROSERVICE_NAME = "api-gateway"

async def log_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    # Attach request_id to response header for downstream tracing
    request.state.request_id = request_id
    method = request.method
    path = request.url.path
    params = dict(request.query_params)
    # Try to get body if possible (exclude sensitive fields)
    body_params = {}
    if method in ("POST", "PUT", "PATCH"):  # Only parse body for relevant methods
        try:
            body = await request.json()
            body_params = {k: ("***" if k in SENSITIVE_FIELDS else v) for k, v in body.items()}
        except Exception as e:
            root_logger.warning(
                "Failed to parse request body",
                extra={
                    "error": str(e)
                }
            )
    # Merge query and body params
    all_params = {**params, **body_params}
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as exc:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        root_logger.error(
            "Request failed",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration": round((time.time() - start_time) * 1000, 2),
                "params": all_params,
            },
        )
        raise
    duration = round((time.time() - start_time) * 1000, 2)
    root_logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
            "microservice": MICROSERVICE_NAME,
            "params": all_params,
        },
    )
    # Add X-Request-ID to response for tracing
    if isinstance(response, Response):
        response.headers["X-Request-ID"] = request_id
    return response

