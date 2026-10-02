import os
from typing import ClassVar, Self, cast


class SingletonMeta(type):
    _instances: ClassVar[dict] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Configuration(SingletonMeta):
    def __init__(cls):
        env_var = os.getenv("ENVIRONMENT")
        if env_var is None:
            msg = "ENVIRONMENT variable not set"
            raise ValueError(msg)

        cls.environment: str = env_var


class ApplicationState:
    _instances: ClassVar[dict] = {}

    def __new__(cls) -> Self:
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)

        return cast("Self", cls._instances[cls])
