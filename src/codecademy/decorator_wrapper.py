
from time import perf_counter


def decorator_timer(some_function):

    def wrapper(*args, **kwargs):
        t1 = perf_counter()
        result = some_function(*args, **kwargs)
        end = perf_counter() - t1
        return result, end

    return wrapper


@decorator_timer
def my_pow(a: float, b: float) -> float:
    res = a**b
    return res
