from typing import Protocol


class AbstractEncrypt(Protocol):
    def encrypt(self, plain_text: str) -> str: ...

    def decrypt(self, encrypted_text: str) -> str: ...
