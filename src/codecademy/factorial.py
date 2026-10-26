from functools import lru_cache


@lru_cache
def fact(n: int) -> int:
    if n < 0:
        msg = "Factorial is not defined for negative numbers"
        raise ValueError(msg)

    if n == 0:
        return 1
    else:
        return n * fact(n - 1)


@lru_cache
def fact_itr(n: int) -> int:
    if n < 0:
        msg = "Factorial is not defined for negative numbers"
        raise ValueError(msg)

    fact = 1
    for i in range(1, n + 1):
        fact = fact * i
    return fact
