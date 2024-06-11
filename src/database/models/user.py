from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import Index

from src.database.models.base import Base
from src.database.models.base.mixins import ModelWithTimeMixin, ModelWithUUIDMixin


class User(ModelWithUUIDMixin, ModelWithTimeMixin, Base):
    login: Mapped[str] = mapped_column()
    password: Mapped[str]

    __table_args__ = (Index("idx_lower_login", func.lower(login), unique=True),)
