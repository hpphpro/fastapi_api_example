from typing import Any

import src.common.dto as dto
from src.api.v1.handlers.commands.base import Command
from src.services.gateway import ServiceGateway


class CreateUserCommand(Command[dto.CreateUser, dto.User]):
    __slots__ = ("_gateway",)

    def __init__(self, gateway: ServiceGateway) -> None:
        self._gateway = gateway

    async def execute(self, query: dto.CreateUser, **kwargs: Any) -> dto.User:
        async with self._gateway:
            await self._gateway.database.manager.create_transaction()
            
            return await self._gateway.user().create(query, **kwargs)
