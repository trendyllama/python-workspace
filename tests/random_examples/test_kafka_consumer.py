import logging
from types import SimpleNamespace

from random_examples import kafka_consumer


def test_consume_messages_logs_records_and_closes_consumer(monkeypatch, caplog):
    closed = []

    class FakeConsumer:
        def __init__(self, topic, **kwargs):
            assert topic == "messages"
            assert kwargs == {
                "bootstrap_servers": "localhost:9092",
                "auto_offset_reset": "earliest",
                "group_id": "demo-consumer",
            }

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.close()

        def __iter__(self):
            return iter(
                [
                    SimpleNamespace(
                        topic="messages",
                        value="caf\u00e9".encode("utf-8"),
                        partition=0,
                        offset=1,
                        timestamp=123,
                    )
                ]
            )

        def close(self):
            closed.append(True)

    monkeypatch.setattr(kafka_consumer, "KafkaConsumer", FakeConsumer)

    with caplog.at_level(logging.INFO, logger=kafka_consumer.__name__):
        kafka_consumer.consume_messages()

    assert "Received from messages: caf\u00e9" in caplog.text
    assert closed == [True]
