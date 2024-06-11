from typing import TypedDict

from typing_extensions import Required


class CreateUserType(TypedDict):
    login: Required[str]
    password: Required[str]
