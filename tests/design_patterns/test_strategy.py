"""
Tests and examples for the strategy pattern.

Strategy allows you to replace one algorithm with another without
changing the context. Unlike the template method pattern, which defines
the steps of an algorithm, the strategy pattern defines the algorithm itself.

Examples:
"""

import pytest

from src.design_patterns.strategy import (
    BubbleSortStrategy,
    Context,
    DefaultSortStrategy,
    QuickSortStrategy,
)


@pytest.mark.parametrize(
    "strategy",
    [
        BubbleSortStrategy(),
        QuickSortStrategy(),
        DefaultSortStrategy(),
    ],
)
@pytest.mark.parametrize(
    ("dataset", "expected"),
    [
        ([3, 1, 2], [1, 2, 3]),
        ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
        ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
        ([1, 3, 2, 5, 4], [1, 2, 3, 4, 5]),
    ],
)
def test_sort_strategy_with_parametrize(strategy, dataset, expected):
    """
    Test the strategy pattern. By changing the strategy of the context object,
    we can change the sorting algorithm

    this makes the code more flexible and allows us to change
    the sorting algorithm in the future"""
    context = Context(strategy)

    assert strategy.sort(dataset) == expected
    assert context.execute(dataset) == expected
