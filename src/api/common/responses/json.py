from typing import Any, Generic, Mapping, Optional

from fastapi.responses import JSONResponse as _JSONResponse
from starlette.background import BackgroundTask

from src.common.serializers.json import json_dumps
from src.common.types import ResultType


class JSONResponse(_JSONResponse):
    def render(self, content: Any) -> bytes:
        return json_dumps(content)


class OkResponse(JSONResponse, Generic[ResultType]):
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
