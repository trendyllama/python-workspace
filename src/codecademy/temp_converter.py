import logging
from abc import abstractmethod
from decimal import Decimal
from enum import StrEnum
from functools import singledispatch
from typing import Protocol

logger = logging.getLogger(__name__)


class TempatureUnit(StrEnum):
    CELCIUS = "C"
    FAHRENHEIT = "F"


type Numeric = int | float | Decimal

@abstractmethod
@singledispatch
def conversion(temp: Numeric, units: TempatureUnit) -> float | Decimal:
    ...

@conversion.register
def _(temp: float, units: TempatureUnit) -> float:
    match units:
        case TempatureUnit.FAHRENHEIT:
            c = (temp - 32) * (5 / 9)
            return c
        case TempatureUnit.CELCIUS:
            f = (temp * (9 / 5)) + 32
            return f

@conversion.register
def _(temp: int, units: TempatureUnit) -> float:
    match units:
        case TempatureUnit.FAHRENHEIT:
            c = (temp - 32) * (5 / 9)
            return c
        case TempatureUnit.CELCIUS:
            f = (temp * (9 / 5)) + 32
            return f


@conversion.register
def _(temp: Decimal, units: TempatureUnit) -> Decimal:
    match units:
        case TempatureUnit.FAHRENHEIT:
            c = (temp - Decimal(32)) * (Decimal(5) / Decimal(9))
            return c
        case TempatureUnit.CELCIUS:
            f = (temp * (Decimal(9) / Decimal(5))) + Decimal(32)
            return f


class TemperatureConverter(Protocol):
    temperature: float

    def __init__(self, temperature: float) -> None: ...

    def convert(self) -> float: ...


class FahrenheitToCelciusConverter(TemperatureConverter):
    def __init__(self, temperature: float) -> None:
        logger.debug(
            "Initializing FahrenheitToCelciusConverter with temperature: %s",
            temperature,
        )
        self.temperature = temperature

    def convert(self) -> float:
        return (self.temperature - 32) * (5 / 9)


class CelciusToFahrenheitConverter(TemperatureConverter):
    def __init__(self, temperature: float) -> None:
        logger.debug(
            "Initializing CelciusToFahrenheitConverter with temperature: %s",
            temperature,
        )

        self.temperature = temperature

    def convert(self) -> float:
        return (self.temperature * (9 / 5)) + 32


class TemperatureConverterBuilder:
    def __init__(self, units_to: TempatureUnit, units_from: TempatureUnit, temperature: float) -> None:
        self.units_to = units_to
        self.units_from = units_from
        self.temperature = temperature
        logger.debug(
            "Initializing TemperatureConverterBuilder with units_to: %s, units_from: %s, temperature: %s",
            units_to,
            units_from,
            temperature,
        )

    def build(self) -> TemperatureConverter:
        if self.units_to == TempatureUnit.CELCIUS and self.units_from == TempatureUnit.FAHRENHEIT:
            return FahrenheitToCelciusConverter(self.temperature)

        if self.units_to == TempatureUnit.FAHRENHEIT and self.units_from == TempatureUnit.CELCIUS:
            return CelciusToFahrenheitConverter(self.temperature)

        raise NotImplementedError
