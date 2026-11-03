"""An asynchronous order processor with async event listeners.

Run a sample order against a local SMTP server such as Mailpit:

    uv run python -m events.async_order_processor \
        --customer-email ada@example.com --item notebook --total 12.50

Configure SMTP_HOST, SMTP_PORT, SMTP_SENDER, and ORDER_DATABASE_PATH to
override the local-development defaults.
"""

import argparse
import asyncio
import json
import logging
import os
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

import aiosqlite

from events.order_processor import (
    ORDER_PLACED,
    Order,
    OrderEmailService,
)

logger = logging.getLogger(__name__)
AsyncOrderCallback = Callable[[Order], Awaitable[None]]


@dataclass
class AsyncEventBus:
    _listeners: dict[str, list[AsyncOrderCallback]] = field(default_factory=dict)

    def on(self, event_name: str, callback: AsyncOrderCallback) -> None:
        if not event_name:
            message = "event_name cannot be empty"
            raise ValueError(message)
        self._listeners.setdefault(event_name, []).append(callback)

    async def emit(self, event_name: str, order: Order) -> None:
        for callback in tuple(self._listeners.get(event_name, ())):
            await callback(order)


class AsyncOrderProcessor:
    def __init__(self, events: AsyncEventBus) -> None:
        self._events = events

    async def place_order(self, order: Order) -> None:
        await self._events.emit(ORDER_PLACED, order)


class AsyncOrderEmailService:
    def __init__(self, email_service: OrderEmailService) -> None:
        self._email_service = email_service

    async def send_confirmation(self, order: Order) -> None:
        await asyncio.to_thread(self._email_service.send_confirmation, order)


class AsyncOrderDatabaseService:
    def __init__(self, database_path: str | Path = "orders.db") -> None:
        self._database_path = Path(database_path)

    async def initialize(self) -> None:
        async with aiosqlite.connect(self._database_path) as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    customer_email TEXT NOT NULL,
                    items TEXT NOT NULL,
                    total TEXT NOT NULL
                )
                """
            )
            await connection.commit()

    async def save_order(self, order: Order) -> None:
        async with aiosqlite.connect(self._database_path) as connection:
            await connection.execute(
                """
                INSERT INTO orders (order_id, customer_email, items, total)
                VALUES (?, ?, ?, ?)
                """,
                (
                    order.order_id,
                    order.customer_email,
                    json.dumps(order.items),
                    str(order.total),
                ),
            )
            await connection.commit()


class AsyncOrderTransactionLogger:
    async def log_order(self, order: Order) -> None:
        logger.info(
            "Order %s placed with %d item(s), total %s",
            order.order_id,
            len(order.items),
            order.total,
        )


async def build_async_order_processor(
    database_path: str | Path = "orders.db",
    smtp_host: str = "localhost",
    smtp_port: int = 1025,
    sender_email: str = "orders@example.com",
    smtp_username: str | None = None,
    smtp_password: str | None = None,
    smtp_use_tls: bool = False,
) -> AsyncOrderProcessor:
    events = AsyncEventBus()
    email_service = AsyncOrderEmailService(
        OrderEmailService(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            sender_email=sender_email,
            username=smtp_username,
            password=smtp_password,
            use_tls=smtp_use_tls,
        )
    )
    database_service = AsyncOrderDatabaseService(database_path)
    await database_service.initialize()
    transaction_logger = AsyncOrderTransactionLogger()

    events.on(ORDER_PLACED, database_service.save_order)
    events.on(ORDER_PLACED, email_service.send_confirmation)
    events.on(ORDER_PLACED, transaction_logger.log_order)

    return AsyncOrderProcessor(events)


async def _place_order(args: argparse.Namespace) -> None:
    processor: AsyncOrderProcessor = await build_async_order_processor(
        database_path=os.getenv("ORDER_DATABASE_PATH", "orders.db"),
        smtp_host=os.getenv("SMTP_HOST", "localhost"),
        smtp_port=int(os.getenv("SMTP_PORT", "1025")),
        sender_email=os.getenv("SMTP_SENDER", "orders@example.com"),
        smtp_username=os.getenv("SMTP_USERNAME"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        smtp_use_tls=os.getenv("SMTP_USE_TLS", "").lower() == "true",
    )
    await processor.place_order(
        Order(
            order_id=uuid.uuid4().hex,
            customer_email=args.customer_email,
            items=tuple(args.item),
            total=args.total,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Place an order asynchronously.")
    parser.add_argument("--customer-email", required=True)
    parser.add_argument("--item", action="append", required=True)
    parser.add_argument("--total", required=True, type=Decimal)
    args: argparse.Namespace = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    asyncio.run(_place_order(args))


if __name__ == "__main__":
    main()
