import importlib

from src.common.dto.base import DTO
from src.common.dto.status import Status
from src.common.dto.token import Token, Tokens, TokensExpire
from src.common.dto.user import CreateUser, Fingerprint, User, UserLogin


# this is a hack for recursive imports pydantic types
def rebuild_models() -> None:
    module = importlib.import_module(__name__)
    for model_name in set(__all__):
        model = getattr(module, model_name, None)
        if model and issubclass(model, DTO):
            model.model_rebuild()


__all__ = (
    "DTO",
    "Token",
    "Tokens",
    "User",
    "CreateUser",
    "Status",
    "UserLogin",
    "TokensExpire",
    "Fingerprint",
)

# this should be unchanged
rebuild_models()
