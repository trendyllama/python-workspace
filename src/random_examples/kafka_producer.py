import argparse
import logging
import time
from typing import TYPE_CHECKING

from kafka import KafkaProducer

from random_examples.kafka_config import (
    DEFAULT_BOOTSTRAP_SERVERS,
    DEFAULT_PRODUCER_TIMEOUT_SECONDS,
    DEFAULT_TOPIC,
)

if TYPE_CHECKING:
    from kafka.producer.future import RecordMetadata

LOGGER = logging.getLogger(__name__)


def send_message(
    message: str,
    topic: str = DEFAULT_TOPIC,
    bootstrap_servers: str = DEFAULT_BOOTSTRAP_SERVERS,
) -> None:

    with KafkaProducer(bootstrap_servers=bootstrap_servers) as producer:
        _send_message(producer, message, topic)


def publish_messages(
    message: str,
    topic: str = DEFAULT_TOPIC,
    bootstrap_servers: str = DEFAULT_BOOTSTRAP_SERVERS,
    interval_seconds: float = 5,
) -> None:
    if interval_seconds <= 0:
        error_message = "interval_seconds must be greater than zero"
        raise ValueError(error_message)

    with KafkaProducer(bootstrap_servers=bootstrap_servers) as producer:
        while True:
            _send_message(producer, message, topic)
            time.sleep(interval_seconds)


def _send_message(producer: KafkaProducer, message: str, topic: str) -> None:
    metadata: RecordMetadata = producer.send(topic, message.encode("utf-8")).get(
        timeout=DEFAULT_PRODUCER_TIMEOUT_SECONDS
    )
    LOGGER.info(
        "Sent message",
        extra={
            "partition": metadata.partition,
            "offset": metadata.offset,
            "timestamp": metadata.timestamp,
            "topic": metadata.topic,
            "content": message,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a message to Kafka.")
    parser.add_argument("message", help="Text message to send.")
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--bootstrap-servers", default=DEFAULT_BOOTSTRAP_SERVERS)
    parser.add_argument(
        "--repeat",
        action="store_true",
        help="Keep publishing the message until the process is stopped.",
    )
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=5,
        help="Delay between repeated messages (default: 5 seconds).",
    )
    args: argparse.Namespace = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    if args.repeat:
        publish_messages(
            args.message, args.topic, args.bootstrap_servers, args.interval_seconds
        )
    else:
        send_message(args.message, args.topic, args.bootstrap_servers)


if __name__ == "__main__":
    main()
