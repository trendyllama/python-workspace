import asyncio
import datetime as dt
from typing import Any, Protocol


class DiffSubscriber(Protocol):
    async def receive_diff(self, diff: dict[str, Any]) -> Any: ...


class Publisher(Protocol):
    async def subscribe(self, subscriber: DiffSubscriber) -> None: ...

    async def unsubscribe(self, subscriber: DiffSubscriber) -> None: ...


class Config[Index: int](Publisher):
    def __init__(self):
        self._data: dict[str, Any] = {}
        self._diffs: dict[tuple[str, int], dict[str, Any]] = {}
        self._subscribers: list[DiffSubscriber] = []
        self._lock = asyncio.Lock()

    async def snapshot(self):
        # Simulate taking a snapshot of the current configuration
        async with self._lock:
            return (
                self._data.copy(),
                self._diffs.copy(),
                dt.datetime.now(dt.UTC),
            )

    async def get(self, key: str):
        async with self._lock:
            return self._data.get(key, None)

    async def subscribe(self, subscriber: DiffSubscriber) -> None:
        async with self._lock:
            self._subscribers.append(subscriber)

    async def unsubscribe(self, subscriber: DiffSubscriber) -> None:
        async with self._lock:
            self._subscribers.remove(subscriber)

    async def _notify_diff_listeners(self, diff: dict[str, Any]) -> None:
        async with self._lock:
            subscribers = list(self._subscribers)

        for subscriber in subscribers:
            await subscriber.receive_diff(diff)

    async def put(self, key: str, value: Any):
        async with self._lock:
            old_value = self._data.get(key, None)
            self._data[key] = value

            max_idx = max((idx for (_, idx) in self._diffs), default=0)
            version = max_idx + 1
            diff: dict[str, Any] = {
                "key": key,
                "old": old_value,
                "new": value,
                "version": version,
            }
            self._diffs[(key, version)] = diff

        await self._notify_diff_listeners(diff)

    async def get_diffs(self) -> list[dict[str, Any]]:
        async with self._lock:
            return list(self._diffs.values())
