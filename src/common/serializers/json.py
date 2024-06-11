import json
from typing import Any

from src.common.serializers.default import _default, _predict_bytes


def json_dumps(value: Any) -> bytes:
    return (
        _predict_bytes(value)
        or json.dumps(
            value,
            default=_default,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    )
