import logging
from collections.abc import Callable
from typing import Protocol

logger = logging.getLogger(__name__)


class AlgoirthmTemplate(Protocol):
    def step1(self): ...

    def step2(self): ...

    def step3(self): ...


class ConcreteAlgorithm1(AlgoirthmTemplate):
    def step1(self):
        logger.info("ConcreteAlgorithm1 step1")

    def step2(self):
        logger.info("ConcreteAlgorithm1 step2")

    def step3(self):
        logger.info("ConcreteAlgorithm1 step3")


class ConcreteAlgorithm2(AlgoirthmTemplate):
    def step1(self):
        logger.info("ConcreteAlgorithm2 step1")

    def step2(self):
        logger.info("ConcreteAlgorithm2 step2")

    def step3(self):
        logger.info("ConcreteAlgorithm2 step3")


# Functional approach
def execute_template(step1: Callable, step2: Callable, step3: Callable) -> None:
    step1()
    step2()
    step3()
