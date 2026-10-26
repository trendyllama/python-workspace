import pytest

from src.codecademy.recursive_multiplication import multiplication, recursive_sum


@pytest.mark.parametrize(
    ("n", "m", "expected"),
    [(3, 7, 21), (5, 5, 25), (0, 4, 0)],
)
def test_multiplication(n: int, m: int, expected: int) -> None:
    assert multiplication(n, m) == expected


@pytest.mark.parametrize(
    ("n", "m", "expected"),
    [(1, 2, 3), (5, 7, 12), (30, 12, 42)],
)
def test_recursive_sum(n: int, m: int, expected: int) -> None:
    assert recursive_sum(n, m) == expected
