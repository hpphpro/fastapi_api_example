import inspect
from typing import (
    Any,
    Dict,
    Optional,
    Protocol,
    Set,
    Type,
    Union,
    get_args,
    get_origin,
    get_overloads,
    get_type_hints,
    overload,
)

import src.common.dto as dto
from src.api.v1.handlers.commands.base import QT, RT, Command, CommandProtocol
from src.api.v1.handlers.commands.mediator import AwaitableProxy, CommandType
from src.api.v1.handlers.commands.user import (
    CreateUserCommand,
    GetUserCommand,
    GetUserQuery,
)
from src.common.interfaces.hasher import AbstractHasher

__all__ = (
    "CreateUserCommand",
    "GetUserQuery",
    "GetUserCommand",
)


class CommandMediatorProtocol(Protocol):
    # there you should add an overload for your command
    # it need to auto registry your command and also typing in routes
    @overload
    def send(
        self, query: dto.CreateUser, *, hasher: AbstractHasher
    ) -> AwaitableProxy[CreateUserCommand, dto.User]: ...
    @overload
    def send(self, query: GetUserQuery) -> AwaitableProxy[GetUserCommand, dto.User]: ...

    # default one, should leave unchanged at the bottom of the protocol
    def send(self, query: QT, **kwargs: Any) -> AwaitableProxy[CommandType, RT]: ...


def _predict_dependency_or_raise(
    actual: Dict[str, Any],
    expectable: Dict[str, Any],
    non_checkable: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    if not non_checkable:
        non_checkable = set()

    missing = [k for k in actual if k not in expectable and k not in non_checkable]
    if missing:
        details = ", ".join(f"`{k}`:`{actual[k]}`" for k in missing)
        raise TypeError(f"Did you forget to set dependency for {details}?")

    return {k: value if (value := expectable.get(k)) else actual[k] for k in actual}


def _retrieve_command_params(command: CommandProtocol) -> Dict[str, Any]:
    return {k: v.annotation for k, v in inspect.signature(command).parameters.items()}


def get_query_commands() -> (
    Dict[Type[dto.DTO], Dict[str, Union[Type[CommandProtocol], Any]]]
):
    commands = {}
    overloads = get_overloads(CommandMediatorProtocol.send)
    for send in overloads:
        hints = get_type_hints(send)
        query, proxy = hints.get("query"), hints.get("return")

        if not query or not proxy:
            raise TypeError(
                "Did you forget to annotate your overloads? "
                "It should contain :query: param and :return: AwaitableProxy generic"
            )
        origin = get_origin(proxy)
        if origin is not AwaitableProxy:
            raise TypeError("Return type must be a type of AwaitableProxy.")

        args = get_args(proxy)

        if len(args) < 2:
            raise TypeError("AwaitableProxy must have two generic parameters")

        command = args[0]
        if not issubclass(command, Command):
            raise TypeError("command must inherit from base Command class.")

        commands[query] = {"command": command, **_retrieve_command_params(command)}

    return commands
