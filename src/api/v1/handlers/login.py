from typing import Annotated, Final

from fastapi import Depends
from fastapi.concurrency import run_in_threadpool

import src.common.dto as dto
from src.api.common.cache.redis import RedisCache
from src.api.common.providers import Stub
from src.common.exceptions import NotFoundError, UnAuthorizedError
from src.common.interfaces.hasher import AbstractHasher
from src.database.gateway import DBGateway
from src.services.security.jwt import TokenJWT

DEFAULT_TOKENS_COUNT: Final[int] = 5


class Login:
    async def __call__(
        self,
        body: dto.UserLogin,
        hasher: Annotated[AbstractHasher, Depends(Stub(AbstractHasher))],
        cache: Annotated[RedisCache, Depends(Stub(RedisCache))],
        jwt: Annotated[TokenJWT, Depends(Stub(TokenJWT))],
        database: Annotated[DBGateway, Depends(Stub(DBGateway))],
    ) -> dto.TokensExpire:
        async with database:
            user = await database.user().get_one(login=body.login)

        if not user:
            raise NotFoundError("User not found")

        if not hasher.verify_password(user.password, body.password):
            raise UnAuthorizedError("Incorrect password")

        _, access = await run_in_threadpool(jwt.create, typ="access", sub=str(user.id))
        expire, refresh = await run_in_threadpool(
            jwt.create, typ="refresh", sub=str(user.id)
        )
        tokens = await cache.get_list(str(user.id))
        if len(tokens) > DEFAULT_TOKENS_COUNT:
            await cache.delete(str(user.id))

        await cache.set_list(str(user.id), f"{body.fingerprint}::{refresh.token}")

        return dto.TokensExpire(
            refresh_expire=expire,
            tokens=dto.Tokens(access=access.token, refresh=refresh.token),
        )
