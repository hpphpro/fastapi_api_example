from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.common.middlewares.process_time import ProcessMiddleware
from src.core.settings import Settings


def setup_global_middlewares(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server.origins,
        allow_credentials=True,
        allow_methods=settings.server.methods,
        allow_headers=settings.server.headers,
    )
    app.add_middleware(ProcessMiddleware)
