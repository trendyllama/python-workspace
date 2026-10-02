"""Tests for the singleton pattern."""

from src.design_patterns.singleton import SingletonMeta


def test_singleton_metaclass_reuses_the_same_instance():
    class MySingleton(metaclass=SingletonMeta):
        pass

    instance1 = MySingleton()
    instance2 = MySingleton()

    assert instance1 is instance2
    assert instance1 == instance2
