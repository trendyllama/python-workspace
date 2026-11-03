import json
import logging
import sqlite3
from decimal import Decimal
from email.message import EmailMessage
from typing import ClassVar, Self

import pytest

from events.order_processor import (
    ORDER_PLACED,
    EventBus,
    Order,
    build_order_processor,
)


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


def test_event_bus_calls_each_registered_listener() -> None:
    events = EventBus()
    received: list[Order] = []
    order = Order("order-1", "ada@example.com", ("book",), Decimal("12.50"))

    events.on(ORDER_PLACED, received.append)
    events.on(ORDER_PLACED, received.append)
    events.emit(ORDER_PLACED, order)

    assert received == [order, order]


def test_order_processor_runs_database_email_and_log_listeners(
    tmp_path, monkeypatch, caplog
) -> None:
    FakeSMTP.messages.clear()
    monkeypatch.setattr("events.order_processor.smtplib.SMTP", FakeSMTP)
    caplog.set_level(logging.INFO, logger="events.order_processor")
    processor = build_order_processor(database_path=tmp_path / "orders.db")
    order = Order(
        "order-2",
        "ada@example.com",
        ("notebook", "pen"),
        Decimal("15.75"),
    )

    processor.place_order(order)

    with sqlite3.connect(tmp_path / "orders.db") as connection:
        row = connection.execute(
            "SELECT order_id, customer_email, items, total FROM orders"
        ).fetchone()

    assert row == (
        "order-2",
        "ada@example.com",
        json.dumps(["notebook", "pen"]),
        "15.75",
    )
    assert len(FakeSMTP.messages) == 1
    assert FakeSMTP.messages[0]["To"] == "ada@example.com"
    assert "Order order-2 placed" in caplog.text


@pytest.mark.parametrize(
    ("order_id", "customer_email", "items", "total", "error"),
    [
        ("", "ada@example.com", ("book",), Decimal("12.50"), "order_id"),
        ("order-3", "", ("book",), Decimal("12.50"), "customer_email"),
        ("order-3", "ada@example.com", (), Decimal("12.50"), "at least one item"),
        (
            "order-3",
            "ada@example.com",
            ("book",),
            Decimal("-0.01"),
            "cannot be negative",
        ),
    ],
)
def test_order_rejects_invalid_values(
    order_id: str,
    customer_email: str,
    items: tuple[str, ...],
    total: Decimal,
    error: str,
) -> None:
    with pytest.raises(ValueError, match=error):
        Order(order_id, customer_email, items, total)


def test_event_bus_does_not_run_listeners_for_other_events() -> None:
    events = EventBus()
    received: list[Order] = []
    events.on(ORDER_PLACED, received.append)

    order = Order("order-4", "ada@example.com", ("book",), Decimal(1))
    events.emit("order_cancelled", order)

    assert received == []
