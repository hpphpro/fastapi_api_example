import abc
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

QT = TypeVar("QT")
RT = TypeVar("RT")


@runtime_checkable
class CommandProtocol(Protocol):
    def __init__(self, **dependencies: Any) -> None: ...
    async def __call__(self, query: Any, **kwargs: Any) -> Any: ...
    async def execute(self, query: Any, **kwargs: Any) -> Any: ...


class Command(CommandProtocol, Generic[QT, RT]):
    __slots__ = ()

    async def __call__(self, query: QT, **kwargs: Any) -> RT:
        return await self.execute(query, **kwargs)

    @abc.abstractmethod
    async def execute(self, query: QT, **kwargs: Any) -> RT:
        raise NotImplementedError
