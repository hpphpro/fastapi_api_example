from functools import partial
from typing import Awaitable, Callable

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.requests import Request

from src.api.common.responses import DefaultJSONResponse
from src.common.exceptions import (
    AppException,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ServiceNotImplementedError,
    ServiceUnavailableError,
    TooManyRequestsError,
    UnAuthorizedError,
)
from src.core.logger import log


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        UnAuthorizedError, error_handler(status.HTTP_401_UNAUTHORIZED)
    )
    app.add_exception_handler(ConflictError, error_handler(status.HTTP_409_CONFLICT))
    app.add_exception_handler(ForbiddenError, error_handler(status.HTTP_403_FORBIDDEN))
    app.add_exception_handler(NotFoundError, error_handler(status.HTTP_404_NOT_FOUND))
    app.add_exception_handler(
        BadRequestError, error_handler(status.HTTP_400_BAD_REQUEST)
    )
    app.add_exception_handler(
        TooManyRequestsError, error_handler(status.HTTP_429_TOO_MANY_REQUESTS)
    )
    app.add_exception_handler(
        ServiceUnavailableError, error_handler(status.HTTP_503_SERVICE_UNAVAILABLE)
    )
    app.add_exception_handler(
        ServiceNotImplementedError, error_handler(status.HTTP_501_NOT_IMPLEMENTED)
    )
    app.add_exception_handler(
        AppException, error_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, unknown_exception_handler)


async def unknown_exception_handler(
    request: Request, err: Exception
) -> DefaultJSONResponse:
    log.error("Handle error")
    log.exception(f"Unknown error occurred -> {err.args}")
    return DefaultJSONResponse(
        {"status": 500, "message": "Unknown Error"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def validation_exception_handler(
    request: Request, err: RequestValidationError
) -> DefaultJSONResponse:
    log.error(f"Handle error: {type(err).__name__}")
    return DefaultJSONResponse(
        {
            "status": 400,
            "detail": [err.get("msg") for err in err._errors],
            "additional": [err.get("ctx") for err in err._errors],
        },
        status_code=status.HTTP_400_BAD_REQUEST,
    )


def error_handler(
    status_code: int,
) -> Callable[..., Awaitable[DefaultJSONResponse]]:
    return partial(app_error_handler, status_code=status_code)


async def app_error_handler(
    request: Request, err: AppException, status_code: int
) -> DefaultJSONResponse:
    return await handle_error(
        request=request,
        err=err,
        status_code=status_code,
    )


async def handle_error(
    request: Request,
    err: AppException,
    status_code: int,
) -> DefaultJSONResponse:
    log.error(f"Handle error: {type(err).__name__}")
    error_data = err.as_dict()

    return DefaultJSONResponse(**error_data, status_code=status_code)
