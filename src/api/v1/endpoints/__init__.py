from fastapi import APIRouter, FastAPI

from src.api.v1.endpoints.auth import auth_router
from src.api.v1.endpoints.healthcheck import healthcheck_router
from src.api.v1.endpoints.user import user_router

router = APIRouter()
router.include_router(healthcheck_router)
router.include_router(auth_router)
router.include_router(user_router)


def setup_routers(app: FastAPI) -> None:
    app.include_router(router)
