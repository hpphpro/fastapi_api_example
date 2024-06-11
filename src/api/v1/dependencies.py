from typing import Callable, TypeVar

from fastapi import FastAPI

from src.api.common.cache.redis import RedisCache, get_redis
from src.api.v1.handlers.commands import CommandMediatorProtocol
from src.api.v1.handlers.commands.mediator import CommandMediator
from src.api.v1.handlers.commands.setup import setup_command_mediator
from src.common.interfaces.hasher import AbstractHasher
from src.core.settings import Settings
from src.database import DBGateway, create_database_factory
from src.database.core.connection import create_sa_engine, create_sa_session_factory
from src.database.core.manager import TransactionManager
from src.services import create_service_gateway_factory
from src.services.security.argon2 import get_argon2_hasher
from src.services.security.jwt import TokenJWT

DependencyType = TypeVar("DependencyType")


def singleton(value: DependencyType) -> Callable[[], DependencyType]:
    def singleton_factory() -> DependencyType:
        return value

    return singleton_factory


def setup_dependencies(app: FastAPI, settings: Settings) -> None:
    engine = create_sa_engine(
        settings.db.url,
        pool_size=settings.db.connection_pool_size,
        max_overflow=settings.db.connection_max_overflow,
        pool_pre_ping=settings.db.connection_pool_pre_ping,
    )
    app.state.engine = engine
    session_factory = create_sa_session_factory(engine)
    database_factory = create_database_factory(TransactionManager, session_factory)
    service_factory = create_service_gateway_factory(database_factory)
    redis = get_redis(settings.redis)
    jwt = TokenJWT(settings.ciphers)
    hasher = get_argon2_hasher()

    mediator = CommandMediator()
    setup_command_mediator(
        mediator,
        gateway=service_factory,
        settings=settings,
        cache=redis,
        jwt=jwt,
        hasher=hasher,
    )

    app.dependency_overrides[CommandMediatorProtocol] = singleton(mediator)
    app.dependency_overrides[RedisCache] = singleton(redis)
    app.dependency_overrides[TokenJWT] = singleton(jwt)
    app.dependency_overrides[DBGateway] = database_factory
    app.dependency_overrides[AbstractHasher] = singleton(hasher)
