from random import randrange
from typing import Protocol

from .types import Ordered


class IQuickSort(Protocol):
    def sort(self): ...


def quicksort[T: Ordered](list_input: list[T], start: int, end: int) -> None:
    """
    - inelegant implementation of quicksort

    Examples:
    >>> list_input = [3, 6, 8, 10, 1, 2, 1]
    >>> quicksort(list_input, 0, len(list_input) - 1)
    >>> print(list_input)
    [1, 1, 2, 3, 6, 8, 10]
    """

    # this portion of list has been sorted
    if start >= end:
        return

    # select random element to be pivot

    pivot_idx = randrange(start, end + 1)
    pivot_element = list_input[pivot_idx]

    # swap random element with last element in sub-lists
    list_input[end], list_input[pivot_idx] = list_input[pivot_idx], list_input[end]

    # tracks all elements which should be to left (lesser than) pivot
    less_than_pointer = start

    for i in range(start, end):
        # we found an element out of place
        if list_input[i] < pivot_element:
            # swap element to the right-most portion of lesser elements
            list_input[i], list_input[less_than_pointer] = (
                list_input[less_than_pointer],
                list_input[i],
            )
            # tally that we have one more lesser element
            less_than_pointer += 1
    # move pivot element to the right-most portion of lesser elements
    list_input[end], list_input[less_than_pointer] = (
        list_input[less_than_pointer],
        list_input[end],
    )
    # recursively sort left and right sub-lists
    quicksort(list_input, start, less_than_pointer - 1)
    quicksort(list_input, less_than_pointer + 1, end)
