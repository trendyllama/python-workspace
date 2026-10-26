from functools import reduce


def larger_sum(lst1: list[int], lst2: list[int]) -> tuple[int, list[int], int]:
    sum1 = reduce(lambda x, y: x + y, lst1)

    sum2 = reduce(lambda x, y: x + y, lst2)

    return (
        1 if sum1 > sum2 else 2,
        lst1 if sum1 > sum2 else lst2,
        max(sum2, sum1),
    )
