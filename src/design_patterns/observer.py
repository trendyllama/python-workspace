import logging
import sys
from typing import Protocol

logger = logging.getLogger(__name__)


class Message:
    def __init__(self, message_text: str) -> None:
        self.message_text = message_text


class Observer(Protocol):
    def notify(self, message) -> None: ...

    def subscribe(self, user) -> None: ...


class AppObserver(Observer):
    def __init__(self, name: str) -> None:
        self.name = name
        self.users: list[AppUser] = []

    def subscribe(self, user) -> None:
        self.users.append(user)

    def notify(self, message: Message) -> None:
        for user in self.users:
            user.receive_notification(message)


class AppUser:
    observers: list[AppObserver]

    def __init__(self, name: str) -> None:
        self.name = name

    def subscribe(self, observer: AppObserver) -> None:
        self.observers.append(observer)

    def unsubscribe(self, observer: AppObserver) -> None:
        self.observers.remove(observer)

    def receive_notification(self, message: Message) -> None:
        sys.stdout.write(message.message_text + "\n")
