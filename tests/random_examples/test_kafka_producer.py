from types import SimpleNamespace

import pytest

from random_examples import kafka_producer


def test_send_message_sends_utf8_and_closes_producer(monkeypatch):
    sent = []
    closed = []

    class FakeFuture:
        def get(self, timeout):
            assert timeout == 10
            return SimpleNamespace(topic="messages", partition=0, offset=3)

    class FakeProducer:
        def __init__(self, *, bootstrap_servers):
            assert bootstrap_servers == "localhost:9092"

        def send(self, topic, value):
            sent.append((topic, value))
            return FakeFuture()

        def close(self, *, timeout):
            closed.append(timeout)

    monkeypatch.setattr(kafka_producer, "KafkaProducer", FakeProducer)

    kafka_producer.send_message("caf\u00e9")

    assert sent == [("messages", "caf\u00e9".encode("utf-8"))]
    assert closed == [10]


def test_publish_messages_repeats_until_stopped_and_closes_producer(monkeypatch):
    sent = []
    closed = []
    sleeps = []

    class FakeFuture:
        def get(self, timeout):
            assert timeout == 10
            return SimpleNamespace(topic="messages", partition=0, offset=len(sent))

    class FakeProducer:
        def __init__(self, *, bootstrap_servers):
            assert bootstrap_servers == "localhost:9092"

        def send(self, topic, value):
            sent.append((topic, value))
            return FakeFuture()

        def close(self, *, timeout):
            closed.append(timeout)

    def stop_after_two_messages(interval):
        sleeps.append(interval)
        if len(sleeps) == 2:
            raise KeyboardInterrupt

    monkeypatch.setattr(kafka_producer, "KafkaProducer", FakeProducer)
    monkeypatch.setattr(kafka_producer.time, "sleep", stop_after_two_messages)

    with pytest.raises(KeyboardInterrupt):
        kafka_producer.publish_messages("repeat me", interval_seconds=2)

    assert sent == [("messages", b"repeat me"), ("messages", b"repeat me")]
    assert sleeps == [2, 2]
    assert closed == [10]
