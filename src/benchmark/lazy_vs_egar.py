import argparse
from timeit import repeat

parser = argparse.ArgumentParser()
parser.add_argument("--n", type=int, default=100_000)
parser.add_argument("--number", type=int, default=100)
parser.add_argument("--repeats", type=int, default=5)
args = parser.parse_args()

N = args.n
NUMBER = args.number
REPEATS = args.repeats


def eager_values(n: int) -> list[int]:
    return [i * i for i in range(n)]


def lazy_values(n: int):
    for i in range(n):
        yield i * i


def consume_eagerly() -> int:
    return sum(eager_values(N))


def consume_lazily() -> int:
    return sum(lazy_values(N))


# Check that both approaches produce the same result.
assert consume_eagerly() == consume_lazily()

for name, benchmark in [
    ("return a list, then sum it", consume_eagerly),
    ("yield values, then sum them", consume_lazily),
]:
    times = repeat(benchmark, number=NUMBER, repeat=REPEATS)
    print(f"{name}: best {min(times) / NUMBER:.6f}s per call")
