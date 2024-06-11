import uuid
from typing import Any, overload

import src.common.dto as dto
from src.common.exceptions import ConflictError, NotFoundError
from src.common.interfaces.hasher import AbstractHasher
from src.database.converter import from_model_to_dto
from src.database.repositories import UserRepository
from src.database.tools import on_integrity


class UserService:
    __slots__ = ("_repository",)

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    @on_integrity("login")
    async def create(self, data: dto.CreateUser, hasher: AbstractHasher) -> dto.User:
        data.password = hasher.hash_password(data.password)
        result = await self._repository.create(
            **data.model_dump(exclude={"confirm_password"})
        )

        if not result:
            raise ConflictError("This user already exists")

        return from_model_to_dto(result, dto.User)

    @overload
    async def get_one(self, *, user_id: uuid.UUID) -> dto.User: ...
    @overload
    async def get_one(self, *, login: str) -> dto.User: ...
    async def get_one(self, **kw: Any) -> dto.User:
        result = await self._repository.get_one(**kw)

        if not result:
            raise NotFoundError("User not found")

        return from_model_to_dto(result, dto.User)
