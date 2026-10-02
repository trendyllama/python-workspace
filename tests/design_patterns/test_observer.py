"""
Tests and examples for the observer pattern.

You may have objects that change things in your application and
want to notify other objects about these changes.

"""

import pytest

from src.design_patterns.observer import AppObserver, AppUser, Message


@pytest.fixture
def observer():
    return AppObserver("observer")


def test_observer(observer: AppObserver):
    """
    Test the observer pattern. By resgistering multiple users to an observer,
    we can notify all users of a new message.
    """

    observer.subscribe(AppUser("user1"))
    observer.subscribe(AppUser("user2"))
    observer.subscribe(AppUser("user3"))

    observer.notify(Message("A new feature was just released!"))

    assert len(observer.users) == 3
    assert observer.users[0].name == "user1"
    assert observer.users[1].name == "user2"
    assert observer.users[2].name == "user3"


def test_observer_notifies_subscribers(capsys):
    observer = AppObserver("Observer1")
    user1 = AppUser("User1")
    user2 = AppUser("User2")
    observer.subscribe(user1)
    observer.subscribe(user2)
    message = Message("Hello, Users!")

    observer.notify(message)
    assert capsys.readouterr().out == "Hello, Users!\nHello, Users!\n"

    user1.receive_notification(message)
    user2.receive_notification(message)
    assert capsys.readouterr().out == "Hello, Users!\nHello, Users!\n"
