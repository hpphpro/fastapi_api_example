import uuid
from typing import Annotated, Any, Literal

from fastapi import Depends, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param

from src.api.common.cache.redis import RedisCache
from src.api.common.providers import Stub
from src.common.dto import Fingerprint, Status, Tokens, TokensExpire, User
from src.common.exceptions import ForbiddenError
from src.database import DBGateway
from src.database.converter import from_model_to_dto
from src.services.security.jwt import TokenJWT

TokenType = Literal["access", "refresh"]


class Authorization(SecurityBase):
    def __init__(self, *permissions: Any) -> None:
        self.model = HTTPBearerModel()
        self.scheme_name = type(self).__name__
        self._permission = permissions

    async def __call__(
        self,
        request: Request,
        jwt: Annotated[TokenJWT, Depends(Stub(TokenJWT))],
        database: Annotated[DBGateway, Depends(Stub(DBGateway))],
    ) -> User:
        token = self._get_token(request)
        return await self._verify_token(jwt, database, token, "access")

    async def verify_refresh(
        self,
        body: Fingerprint,
        *,
        request: Request,
        jwt: Annotated[TokenJWT, Depends(Stub(TokenJWT))],
        database: Annotated[DBGateway, Depends(Stub(DBGateway))],
        cache: Annotated[RedisCache, Depends(Stub(RedisCache))],
    ) -> TokensExpire:
        token = request.cookies.get("refresh_token", "")
        user = await self._verify_token(jwt, database, token, "refresh")
        token_pairs = await cache.get_list(str(user.id))
        verified = None
        for pair in token_pairs:
            data = pair.split("::")
            if len(data) < 2:
                await cache.delete(str(user.id))
                raise ForbiddenError(
                    "Broken separator, try to login again. Token is not valid anymore"
                )
            fp, cached_token, *_ = data
            if fp == body.fingerprint and cached_token == token:
                verified = pair
                break

        if not verified:
            await cache.delete(str(user.id))
            raise ForbiddenError("Token is not valid anymore")

        await cache.pop(str(user.id), verified)
        _, access = await run_in_threadpool(jwt.create, typ="access", sub=str(user.id))
        expire, refresh = await run_in_threadpool(
            jwt.create, typ="refresh", sub=str(user.id)
        )
        await cache.set_list(str(user.id), f"{body.fingerprint}::{refresh.token}")

        return TokensExpire(
            refresh_expire=expire,
            tokens=Tokens(access=access.token, refresh=refresh.token),
        )

    async def invalidate_refresh(
        self,
        request: Request,
        jwt: Annotated[TokenJWT, Depends(Stub(TokenJWT))],
        database: Annotated[DBGateway, Depends(Stub(DBGateway))],
        cache: Annotated[RedisCache, Depends(Stub(RedisCache))],
    ) -> Status:
        token = request.cookies.get("refresh_token", "")
        user = await self._verify_token(jwt, database, token, "refresh")
        token_pairs = await cache.get_list(str(user.id))
        for pair in token_pairs:
            data = pair.split("::")
            if len(data) < 2:
                await cache.delete(str(user.id))
                break
            _, cached_token, *_ = data
            if cached_token == token:
                await cache.pop(str(user.id), pair)
                break

        return Status(ok=True)

    async def _verify_token(
        self,
        jwt: TokenJWT,
        database: DBGateway,
        token: str,
        token_type: TokenType,
    ) -> User:
        payload = await run_in_threadpool(jwt.verify_token, token)
        user_id = payload.get("sub")
        actual_token_type = payload.get("type")

        if actual_token_type != token_type:
            raise ForbiddenError("Invalid token")
        async with database:
            user = await database.user().get_one(user_id=uuid.UUID(user_id))

        if not user:
            raise ForbiddenError("Not authenticated")

        return from_model_to_dto(user, User)

    def _get_token(self, request: Request) -> str:
        authorization = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and token):
            raise ForbiddenError("Not authenticated")
        if scheme.lower() != "bearer":
            raise ForbiddenError("Invalid authentication credentials")

        return token
