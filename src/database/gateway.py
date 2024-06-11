from typing import Type

from src.common.interfaces.gateway import BaseGateway
from src.database.core.manager import TransactionManager
from src.database.repositories import UserRepository
from src.database.repositories.types import RepositoryType


class DBGateway(BaseGateway):
    __slots__ = ("manager",)

    def __init__(self, manager: TransactionManager) -> None:
        self.manager = manager
        super().__init__(manager)

    def user(self) -> UserRepository:
        return self._init_repo(UserRepository)

    def _init_repo(self, cls: Type[RepositoryType]) -> RepositoryType:
        return cls(self.manager.session)
