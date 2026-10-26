from decimal import Decimal
from functools import lru_cache, reduce

type Numeric = int | float | Decimal

@lru_cache
def sum_to_n(n: int) -> int:
    if n == 0:
        return 0
    else:
        return n + sum_to_n(n - 1)


@lru_cache
def sum_to_n_functional(n: int) -> int:
    sum_out = reduce(lambda x, y: x + y, range(n + 1))

    return sum_out
