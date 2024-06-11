from typing import Any, Callable, Dict, Generator, Generic, Type, TypeVar, Union, cast

from src.api.v1.handlers.commands.base import QT, RT, CommandProtocol

CommandType = TypeVar("CommandType", bound=CommandProtocol)


class AwaitableProxy(Generic[CommandType, RT]):
    __slots__ = (
        "_command",
        "_kw",
    )

    def __init__(self, command: CommandType, **kw: Any) -> None:
        self._command = command
        self._kw = kw

    def __await__(self) -> Generator[None, None, RT]:
        result = yield from self._command(**self._kw).__await__()
        return cast(RT, result)


def _resolve_factory(
    command_or_factory: Union[Callable[[], CommandProtocol], CommandProtocol],
) -> CommandProtocol:
    if isinstance(command_or_factory, CommandProtocol):
        return command_or_factory
    return command_or_factory()


class CommandMediator:
    def __init__(self) -> None:
        self._commands: Dict[
            Type[Any], Union[Callable[[], CommandProtocol], CommandProtocol]
        ] = {}

    def add(
        self,
        query: Type[QT],
        command_or_factory: Union[Callable[[], CommandProtocol], CommandProtocol],
    ) -> None:
        self._commands[query] = command_or_factory

    def send(self, query: QT, **kwargs: Any) -> AwaitableProxy[CommandProtocol, RT]:
        handler = _resolve_factory(self._commands[type(query)])
        return AwaitableProxy(handler, query=query, **kwargs)
