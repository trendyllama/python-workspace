import argparse
import logging

from kafka import KafkaConsumer

from random_examples.kafka_config import (
    DEFAULT_AUTO_OFFSET_RESET,
    DEFAULT_BOOTSTRAP_SERVERS,
    DEFAULT_CONSUMER_GROUP_ID,
    DEFAULT_TOPIC,
)

LOGGER = logging.getLogger(__name__)


def consume_messages(
    topic: str = DEFAULT_TOPIC,
    bootstrap_servers: str = DEFAULT_BOOTSTRAP_SERVERS,
    group_id: str = DEFAULT_CONSUMER_GROUP_ID,
) -> None:

    with KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset=DEFAULT_AUTO_OFFSET_RESET.value,
        group_id=group_id,
    ) as consumer:
        for message in consumer:
            LOGGER.info(
                "Received from %s: %s",
                message.topic,
                message.value.decode("utf-8"),
                extra={
                    "partition": message.partition,
                    "offset": message.offset,
                    "timestamp": message.timestamp,
                    "topic": message.topic,
                }
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Read messages from Kafka.")
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--bootstrap-servers", default=DEFAULT_BOOTSTRAP_SERVERS)
    parser.add_argument("--group-id", default=DEFAULT_CONSUMER_GROUP_ID)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    consume_messages(args.topic, args.bootstrap_servers, args.group_id)


if __name__ == "__main__":
    main()
