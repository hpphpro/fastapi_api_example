from typing import Any, Callable, Type, Union

from src.api.v1.handlers.commands import _predict_dependency_or_raise, get_query_commands
from src.api.v1.handlers.commands.base import CommandProtocol
from src.api.v1.handlers.commands.mediator import CommandMediator


def create_command_lazy(
    command: Type[CommandProtocol], **dependencies: Union[Callable[[], Any], Any]
) -> Callable[[], CommandProtocol]:
    def _create() -> CommandProtocol:
        return command(
            **{k: v() if callable(v) else v for k, v in dependencies.items()}
        )

    return _create


def setup_command_mediator(mediator: CommandMediator, **kw: Any) -> None:
    for query, command in get_query_commands().items():
        mediator.add(
            query=query,
            command_or_factory=create_command_lazy(
                **_predict_dependency_or_raise(command, kw, {"command"})
            ),
        )
