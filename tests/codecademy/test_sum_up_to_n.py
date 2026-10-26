import pytest

from src.codecademy.sum_up_to_n import sum_to_n, sum_to_n_functional


@pytest.mark.parametrize(("n", "expected"), [(4, 10), (5, 15), (20, 210), (100, 5050)])
def test_sum_to_n(n: int, expected: int) -> None:
    assert sum_to_n(n) == expected


@pytest.mark.parametrize(("n", "expected"), [(4, 10), (5, 15), (20, 210), (100, 5050)])
def test_sum_to_n_functional(n: int, expected: int) -> None:
    assert sum_to_n_functional(n) == expected
