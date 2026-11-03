"""A small order processor with synchronous event listeners.

Run a sample order against a local SMTP server such as Mailpit:

    uv run python -m events.order_processor \
        --customer-email ada@example.com --item notebook --total 12.50

Configure SMTP_HOST, SMTP_PORT, SMTP_SENDER, and ORDER_DATABASE_PATH to
override the local-development defaults.
"""
from typing import Self

import argparse
import json
import logging
import os
import smtplib
import sqlite3
import uuid
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass, field
from decimal import Decimal
from email.message import EmailMessage
from pathlib import Path

ORDER_PLACED = "order_placed"
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Order:
    order_id: str
    customer_email: str
    items: tuple[str, ...]
    total: Decimal

    def __post_init__(self) -> None:
        if not self.order_id:
            message = "order_id cannot be empty"
            raise ValueError(message)
        if not self.customer_email:
            message = "customer_email cannot be empty"
            raise ValueError(message)
        if not self.items:
            message = "an order must contain at least one item"
            raise ValueError(message)
        if self.total < 0:
            message = "order total cannot be negative"
            raise ValueError(message)


OrderCallback = Callable[[Order], None]


@dataclass
class EventBus:
    _listeners: dict[str, list[OrderCallback]] = field(default_factory=dict)

    def on(self, event_name: str, callback: OrderCallback) -> None:
        if not event_name:
            message = "event_name cannot be empty"
            raise ValueError(message)
        self._listeners.setdefault(event_name, []).append(callback)

    def emit(self, event_name: str, order: Order) -> None:
        for callback in tuple(self._listeners.get(event_name, ())):
            callback(order)


class OrderProcessor:
    def __init__(self, events: EventBus) -> None:
        self._events = events

    def place_order(self, order: Order) -> None:
        self._events.emit(ORDER_PLACED, order)


class OrderEmailService:
    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 1025,
        sender_email: str = "orders@example.com",
        timeout: float = 10.0,
        use_tls: bool = False,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        if (username is None) != (password is None):
            message = "SMTP username and password must be provided together"
            raise ValueError(message)
        if username is not None and not use_tls:
            message = "SMTP authentication requires TLS"
            raise ValueError(message)
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._sender_email = sender_email
        self._timeout = timeout
        self._use_tls = use_tls
        self._username = username
        self._password = password

    def send_confirmation(self, order: Order) -> None:
        message = EmailMessage()
        message["Subject"] = f"Order confirmation: {order.order_id}"
        message["From"] = self._sender_email
        message["To"] = order.customer_email
        message.set_content(
            f"Thanks for your order!\n\n"
            f"Order: {order.order_id}\n"
            f"Items: {', '.join(order.items)}\n"
            f"Total: {order.total:.2f}\n"
        )

        with smtplib.SMTP(
            self._smtp_host, self._smtp_port, timeout=self._timeout
        ) as smtp:
            if self._use_tls:
                smtp.starttls()
            if self._username is not None and self._password is not None:
                smtp.login(self._username, self._password)
            smtp.send_message(message)


class OrderDatabaseService:
    def __init__(self, database_path: str | Path = "orders.db") -> None:
        self._database_path = Path(database_path)

        self._connection = sqlite3.connect(self._database_path)


        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    customer_email TEXT NOT NULL,
                    items TEXT NOT NULL,
                    total TEXT NOT NULL
                )
                """
            )

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def save_order(self, order: Order) -> None:
        with self._connection:
            self._connection.execute(
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


class OrderTransactionLogger:
    def log_order(self, order: Order) -> None:
        logger.info(
            "Order %s placed with %d item(s), total %s",
            order.order_id,
            len(order.items),
            order.total,
        )


def build_order_processor(
    database_path: str | Path = "orders.db",
    smtp_host: str = "localhost",
    smtp_port: int = 1025,
    sender_email: str = "orders@example.com",
    smtp_username: str | None = None,
    smtp_password: str | None = None,
    smtp_use_tls: bool = False,
) -> OrderProcessor:
    events = EventBus()
    email_service = OrderEmailService(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        sender_email=sender_email,
        username=smtp_username,
        password=smtp_password,
        use_tls=smtp_use_tls,
    )
    database_service = OrderDatabaseService(database_path)
    transaction_logger = OrderTransactionLogger()

    events.on(ORDER_PLACED, database_service.save_order)
    events.on(ORDER_PLACED, email_service.send_confirmation)
    events.on(ORDER_PLACED, transaction_logger.log_order)

    return OrderProcessor(events)


def main() -> None:
    parser = argparse.ArgumentParser(description="Place an order.")
    parser.add_argument("--customer-email", required=True)
    parser.add_argument("--item", action="append", required=True)
    parser.add_argument("--total", required=True, type=Decimal)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    processor = build_order_processor(
        database_path=os.getenv("ORDER_DATABASE_PATH", "orders.db"),
        smtp_host=os.getenv("SMTP_HOST", "localhost"),
        smtp_port=int(os.getenv("SMTP_PORT", "1025")),
        sender_email=os.getenv("SMTP_SENDER", "orders@example.com"),
        smtp_username=os.getenv("SMTP_USERNAME"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        smtp_use_tls=os.getenv("SMTP_USE_TLS", "").lower() == "true",
    )
    processor.place_order(
        Order(
            order_id=uuid.uuid4().hex,
            customer_email=args.customer_email,
            items=tuple(args.item),
            total=args.total,
        )
    )


if __name__ == "__main__":
    main()
