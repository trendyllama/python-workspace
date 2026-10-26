import logging
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.engine.base import Engine
    from sqlalchemy.engine.row import Row

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_engine() -> sa.Engine:
    return sa.create_engine("sqlite:///:memory:")


def get_async_engine() -> AsyncEngine:
    return create_async_engine("sqlite+aiosqlite:///:memory:")


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(50), nullable=False)
    email = sa.Column(sa.String(120), unique=True, nullable=False)


def init_db():
    engine: Engine = get_engine()

    with engine.begin() as conn:
        Base.metadata.create_all(conn)
        conn.execute(
            sa.insert(User),
            [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
                {"name": "Alex", "email": "alex@example.com"},
                {"name": "David", "email": "david@example.com"},
            ],
        )

        result: Sequence[Row[User]] = conn.execute(
            sa.select(User).where(User.name.like("Al%")).order_by(User.id)
        ).all()
        logger.debug("Selected users with names starting with 'Al': %s", result)

        for row in result:
            logger.info("User %s: %s, %s", row.id, row.name, row.email)

        conn.execute(sa.delete(User).where(User.name == "Bob"))

        result: Sequence[Row[User]] = conn.execute(sa.select(User).order_by(User.id)).all()
        for row in result:
            logger.info("User %s: %s, %s", row.id, row.name, row.email)
