from functools import lru_cache


@lru_cache
def multiplication(n, m):
    # base case
    if n == 0 or m == 0:
        return 0
    return n + multiplication(n, m - 1)


@lru_cache
def recursive_sum(n: int, m: int) -> int:
    if n == 0:
        return m

    return recursive_sum(n - 1, m + 1)
