# mypy: ignore-errors
import logging
import multiprocessing as mp
from typing import Any, Dict, Optional

from gunicorn.app.base import Application

from src.core.logger import log
from src.core.settings import Settings

system = logging.basicConfig()


def workers_count() -> int:
    return (mp.cpu_count() * 2) + 1


class GunicornApplication(Application):
    def __init__(
        self, app: Any, options: Optional[Dict[str, Any]] = None, **kw: Any
    ) -> None:
        self._options = options or {}
        self._app = app
        super().__init__(**kw)

    def load_config(self) -> None:
        for key, value in self._options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

    def load(self) -> Any:
        return self._app


def run_api_gunicorn(app: Any, settings: Settings, **kwargs: Any) -> None:
    options = {
        "bind": f"{settings.server.host}:{settings.server.port}",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "preload_app": True,
        "timeout": 3600,
        "workers": workers_count(),
        "accesslog": "-",
        # "worker_connections": 1000,  # 1000 is default value
        # "max_requests": 1000,  
        # "max_requests_jitter": 50, 
        # "threads": 4,
    }
    gunicorn_app = GunicornApplication(app, options | kwargs)
    log.info("Running API Gunicorn")
    gunicorn_app.run()
