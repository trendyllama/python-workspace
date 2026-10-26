from decimal import Decimal

import pytest

from src.codecademy.temp_converter import TempatureUnit, conversion


@pytest.mark.parametrize(
    ("temperature", "units", "expected"),
    [
        (32.0, TempatureUnit.FAHRENHEIT, 0.0),
        (0.0, TempatureUnit.CELCIUS, 32.0),
        (100.0, TempatureUnit.FAHRENHEIT, 37.77777777777778),
        (100.0, TempatureUnit.CELCIUS, 212.0),
    ],
)
def test_conversion_with_float(
    temperature: float, units: TempatureUnit, expected: float
) -> None:
    assert conversion(temperature, units) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("temperature", "units", "expected"),
    [
        (32, TempatureUnit.FAHRENHEIT, 0.0),
        (0, TempatureUnit.CELCIUS, 32.0),
        (100, TempatureUnit.FAHRENHEIT, 37.77777777777778),
        (100, TempatureUnit.CELCIUS, 212.0),
    ],
)
def test_conversion_with_int(
    temperature: int, units: TempatureUnit, expected: float
) -> None:
    assert conversion(temperature, units) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("temperature", "units", "expected"),
    [
        (Decimal(32), TempatureUnit.FAHRENHEIT, Decimal("0.0")),
        (Decimal(0), TempatureUnit.CELCIUS, Decimal("32.0")),
        (
            Decimal(100),
            TempatureUnit.FAHRENHEIT,
            Decimal("37.77777777777777777777777778"),
        ),
        (Decimal(100), TempatureUnit.CELCIUS, Decimal("212.0")),
    ],
)
def test_conversion_with_decimal(
    temperature: Decimal, units: TempatureUnit, expected: Decimal
) -> None:
    assert conversion(temperature, units) == expected
