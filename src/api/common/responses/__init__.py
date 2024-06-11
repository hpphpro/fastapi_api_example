try:
    import orjson  # type: ignore # noqa

    from src.api.common.responses.orjson import OkResponse as OkResponse
    from src.api.common.responses.orjson import ORJSONResponse as DefaultJSONResponse
except ImportError:  # pragma: no cover
    from src.api.responses.json import (  # type: ignore
        JSONResponse as DefaultJSONResponse,
    )
    from src.api.responses.json import OkResponse as OkResponse  # type: ignore


__all__ = (
    "OkResponse",
    "DefaultJSONResponse",
)
