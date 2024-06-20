from __future__ import annotations

import uuid

from src.common.dto.base import DTO


class User(DTO):
    id: uuid.UUID
    login: str


class CreateUser(DTO):
    login: str
    password: str


class Fingerprint(DTO):
    fingerprint: str


class UserLogin(Fingerprint):
    login: str
    password: str
