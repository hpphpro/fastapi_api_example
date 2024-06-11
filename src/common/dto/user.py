from __future__ import annotations

import uuid

from pydantic import model_validator

from src.common.dto.base import DTO


class User(DTO):
    id: uuid.UUID
    login: str


class CreateUser(DTO):
    login: str
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def _validate_password(self) -> CreateUser:
        if self.password != self.confirm_password:
            raise ValueError("Passwords does not match")

        return self

class Fingerprint(DTO):
    fingerprint: str

class UserLogin(Fingerprint):
    login: str
    password: str
