from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.api.common.docs import ForbiddenError, NotFoundError, UnAuthorizedError
from src.api.v1.handlers.auth import Authorization
from src.api.v1.handlers.login import Login
from src.api.common.responses import OkResponse
from src.common.dto import Status, Tokens, TokensExpire

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/login",
    response_model=Tokens,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": NotFoundError},
        status.HTTP_401_UNAUTHORIZED: {"model": UnAuthorizedError},
    },
)
async def login_endpoint(
    login: Annotated[TokensExpire, Depends(Login())],
) -> OkResponse[Tokens]:
    response = OkResponse(login.tokens)
    response.set_cookie(
        "refresh_token",
        value=login.tokens.refresh,
        expires=login.refresh_expire,
        httponly=True,
        secure=True,
    )

    return response


@auth_router.post(
    "/refresh",
    response_model=Tokens,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": UnAuthorizedError},
        status.HTTP_403_FORBIDDEN: {"model": ForbiddenError},
    },
)
async def refresh_endpoint(
    verified: Annotated[TokensExpire, Depends(Authorization().verify_refresh)],
) -> OkResponse[Tokens]:
    response = OkResponse(verified.tokens)
    response.set_cookie(
        "refresh_token",
        value=verified.tokens.refresh,
        expires=verified.refresh_expire,
        httponly=True,
        secure=True,
    )

    return response


@auth_router.post(
    "/logout",
    response_model=Status,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": UnAuthorizedError},
        status.HTTP_403_FORBIDDEN: {"model": ForbiddenError},
    },
)
async def logout_endpoint(
    status: Annotated[Status, Depends(Authorization().invalidate_refresh)],
) -> OkResponse[Status]:
    response = OkResponse(status)
    response.delete_cookie("refresh_token")

    return response
