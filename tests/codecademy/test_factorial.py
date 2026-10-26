import pytest

from src.codecademy.factorial import fact, fact_itr


@pytest.mark.parametrize(
    ("n", "expected"), [(5, 120), (3, 6), (0, 1), (10, 3628800)]
)
def test_fact(n: int, expected: int) -> None:
    assert fact(n) == expected


@pytest.mark.parametrize(
    ("n", "expected"), [(5, 120), (3, 6), (0, 1), (10, 3628800)]
)
def test_fact_itr(n: int, expected: int) -> None:
    assert fact_itr(n) == expected
