from typing import Any, Generic, Mapping, Optional

from fastapi.responses import ORJSONResponse as _ORJSONResponse
from starlette.background import BackgroundTask

from src.common.serializers.orjson import orjson_dumps
from src.common.types import ResultType


class ORJSONResponse(_ORJSONResponse):
    def render(self, content: Any) -> bytes:
        return orjson_dumps(content)


class OkResponse(ORJSONResponse, Generic[ResultType]):
    __slots__ = ()

    def __init__(
        self,
        content: ResultType,
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[BackgroundTask] = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)
