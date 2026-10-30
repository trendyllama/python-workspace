import enum
import os


class AutoOffsetReset(enum.StrEnum):
    EARLIEST = "earliest"
    LATEST = "latest"

DEFAULT_BOOTSTRAP_SERVERS: str = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
)
DEFAULT_TOPIC: str = "messages"
DEFAULT_CONSUMER_GROUP_ID: str = "demo-consumer"
DEFAULT_AUTO_OFFSET_RESET: AutoOffsetReset = AutoOffsetReset.EARLIEST
DEFAULT_PRODUCER_TIMEOUT_SECONDS: int = 10
