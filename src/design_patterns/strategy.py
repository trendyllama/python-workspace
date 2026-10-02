from collections.abc import Callable
from typing import Any, Protocol


class SortStrategy(Protocol):
    def sort(self, dataset: list) -> list: ...


class BubbleSortStrategy(SortStrategy):
    def sort(self, dataset: list) -> list:
        dataset = dataset.copy()

        n = len(dataset)

        for i in range(n):
            for j in range(n - i - 1):
                if dataset[j] > dataset[j + 1]:
                    dataset[j], dataset[j + 1] = dataset[j + 1], dataset[j]

        return dataset


class QuickSortStrategy(SortStrategy):
    def sort(self, dataset):
        dataset = dataset.copy()

        if len(dataset) <= 1:
            return dataset

        pivot = dataset.pop()

        items_greater = []
        items_lower = []

        for item in dataset:
            if item > pivot:
                items_greater.append(item)
            else:
                items_lower.append(item)

        return [*self.sort(items_lower), pivot, *self.sort(items_greater)]


class DefaultSortStrategy(SortStrategy):
    def sort(self, dataset: list) -> list:
        return sorted(dataset)


class Context:
    def __init__(self, strategy: SortStrategy) -> None:
        self.strategy = strategy

    def set_strategy(self, strategy: SortStrategy) -> None:
        self.strategy = strategy

    def execute(self, dataset: list) -> list:
        return self.strategy.sort(dataset)


# Functional approach
def execute_sort_strategy(strategy_function: Callable, dataset: Any):
    return strategy_function(dataset)
