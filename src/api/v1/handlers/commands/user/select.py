import uuid
from typing import Any

import src.common.dto as dto
from src.api.v1.handlers.commands.base import Command
from src.services.gateway import ServiceGateway


class GetUserQuery(dto.DTO):
    user_id: uuid.UUID


class GetUserCommand(Command[GetUserQuery, dto.User]):
    __slots__ = ("_gateway",)

    def __init__(self, gateway: ServiceGateway) -> None:
        self._gateway = gateway

    async def execute(self, query: GetUserQuery, **kwargs: Any) -> dto.User:
        async with self._gateway.database.manager.session:
            return await self._gateway.user().get_one(user_id=query.user_id)
