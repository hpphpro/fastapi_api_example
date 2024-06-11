from typing import Any, Dict

from fastapi import APIRouter, status

healthcheck_router = APIRouter(tags=["healthcheck"])


@healthcheck_router.get(
    "/healthcheck",
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def healthcheck_endpoint() -> Dict[str, Any]:
    return {"ok": True}
