import pytest

from src.codecademy.which_list_is_larger import larger_sum


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        ([1, 2, 3], [4, 5], (2, [4, 5], 9)),
        ([10, 20, 30], [5, 15], (1, [10, 20, 30], 60)),
        ([1, 2], [3, 4, 5], (2, [3, 4, 5], 12)),
    ],
)
def test_larger_sum(
    first: list[int], second: list[int], expected: tuple[int, list[int], int]
) -> None:
    assert larger_sum(first, second) == expected
