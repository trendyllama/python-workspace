import json
import logging
import sqlite3
from decimal import Decimal
from email.message import EmailMessage
from typing import ClassVar, Self

import pytest

from events.async_order_processor import (
    ORDER_PLACED,
    AsyncEventBus,
    AsyncOrderProcessor,
    build_async_order_processor,
)
from events.order_processor import Order


class FakeSMTP:
    messages: ClassVar[list[EmailMessage]] = []

    def __init__(self, host: str, port: int, timeout: float) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def send_message(self, message: EmailMessage) -> None:
        self.messages.append(message)


@pytest.mark.asyncio
async def test_async_event_bus_awaits_each_registered_listener() -> None:
    events = AsyncEventBus()
    received: list[Order] = []
    order = Order("order-5", "ada@example.com", ("book",), Decimal("12.50"))

    async def receive_order(event: Order) -> None:
        received.append(event)

    events.on(ORDER_PLACED, receive_order)
    events.on(ORDER_PLACED, receive_order)
    await events.emit(ORDER_PLACED, order)

    assert received == [order, order]


@pytest.mark.asyncio
async def test_async_processor_runs_database_email_and_log_listeners(
    tmp_path, monkeypatch, caplog
) -> None:
    FakeSMTP.messages.clear()
    monkeypatch.setattr("events.order_processor.smtplib.SMTP", FakeSMTP)
    caplog.set_level(logging.INFO, logger="events.async_order_processor")
    processor = await build_async_order_processor(database_path=tmp_path / "orders.db")
    order = Order(
        "order-6",
        "ada@example.com",
        ("notebook", "pen"),
        Decimal("15.75"),
    )

    await processor.place_order(order)

    with sqlite3.connect(tmp_path / "orders.db") as connection:
        row = connection.execute(
            "SELECT order_id, customer_email, items, total FROM orders"
        ).fetchone()

    assert row == (
        "order-6",
        "ada@example.com",
        json.dumps(["notebook", "pen"]),
        "15.75",
    )
    assert len(FakeSMTP.messages) == 1
    assert FakeSMTP.messages[0]["To"] == "ada@example.com"
    assert "Order order-6 placed" in caplog.text


@pytest.mark.asyncio
async def test_async_order_processor_awaits_event_emission() -> None:
    events = AsyncEventBus()
    processor = AsyncOrderProcessor(events)
    received: list[Order] = []

    async def receive_order(order: Order) -> None:
        received.append(order)

    events.on(ORDER_PLACED, receive_order)
    order = Order("order-7", "ada@example.com", ("book",), Decimal(1))

    await processor.place_order(order)

    assert received == [order]


@pytest.mark.asyncio
async def test_async_event_bus_does_not_run_listeners_for_other_events() -> None:
    events = AsyncEventBus()
    received: list[Order] = []

    async def receive_order(order: Order) -> None:
        received.append(order)

    events.on(ORDER_PLACED, receive_order)
    order = Order("order-8", "ada@example.com", ("book",), Decimal(1))
    await events.emit("order_cancelled", order)

    assert received == []
