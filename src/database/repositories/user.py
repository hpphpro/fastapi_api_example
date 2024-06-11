import uuid
from typing import Optional, Type, overload

from typing_extensions import Unpack

import src.database.models as models
from src.database.exceptions import InvalidParamsError
from src.database.repositories.base import BaseRepository
from src.database.repositories.types.user import CreateUserType


class UserRepository(BaseRepository[models.User]):
    __slots__ = ()

    @property
    def model(self) -> Type[models.User]:
        return models.User

    async def create(self, **data: Unpack[CreateUserType]) -> Optional[models.User]:
        return await self._crud.insert(**data)

    @overload
    async def get_one(self, *, user_id: uuid.UUID) -> Optional[models.User]: ...
    @overload
    async def get_one(self, *, login: str) -> Optional[models.User]: ...
    async def get_one(
        self, *, user_id: Optional[uuid.UUID] = None, login: Optional[str] = None
    ) -> Optional[models.User]:
        if not any([user_id, login]):
            raise InvalidParamsError("at least one identifier must be provided")

        clause = self.model.id == user_id if user_id else self.model.login == login

        return await self._crud.select(clause)
