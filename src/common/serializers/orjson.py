import warnings
from typing import Any

from src.common.serializers.default import _default, _predict_bytes
from src.common.serializers.json import json_dumps

try:
    import orjson as orjson  # type: ignore # noqa
except ImportError:  # pragma: no cover
    orjson = None  # type: ignore


def orjson_dumps(value: Any) -> bytes:
    if not orjson:
        warnings.warn(
            message="orjson is not installed. Consider to install it `pip install orjson`. Using default json serializer",
            stacklevel=1,
        )
        return json_dumps(value)
    return _predict_bytes(value) or orjson.dumps(
        value,
        default=_default,
        option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
    )
