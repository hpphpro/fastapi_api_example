from typing import Annotated

from fastapi import APIRouter, Depends, status

import src.common.dto as dto
from src.api.common.docs import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnAuthorizedError,
)
from src.api.common.providers import Stub
from src.api.common.responses import OkResponse
from src.api.v1.handlers.auth import Authorization
from src.api.v1.handlers.commands import CommandMediatorProtocol, GetUserQuery
from src.common.interfaces.hasher import AbstractHasher

user_router = APIRouter(prefix="/users", tags=["user"])


@user_router.post(
    "",
    response_model=dto.User,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"model": ConflictError},
    },
)
async def create_user_endpoint(
    body: dto.CreateUser,
    mediator: Annotated[
        CommandMediatorProtocol, Depends(Stub(CommandMediatorProtocol))
    ],
    hasher: Annotated[AbstractHasher, Depends(Stub(AbstractHasher))],
) -> OkResponse[dto.User]:
    result = await mediator.send(body, hasher=hasher)
    return OkResponse(result, status_code=status.HTTP_201_CREATED)


@user_router.get(
    "/me",
    response_model=dto.User,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": NotFoundError},
        status.HTTP_401_UNAUTHORIZED: {"model": UnAuthorizedError},
        status.HTTP_403_FORBIDDEN: {"model": ForbiddenError},
    },
)
async def get_me_endpoint(
    user: Annotated[dto.User, Depends(Authorization())],
    mediator: Annotated[
        CommandMediatorProtocol, Depends(Stub(CommandMediatorProtocol))
    ],
) -> OkResponse[dto.User]:
    result = await mediator.send(GetUserQuery(user_id=user.id))
    return OkResponse(result)
