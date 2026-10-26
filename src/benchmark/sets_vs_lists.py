import argparse
from timeit import repeat

parser = argparse.ArgumentParser()
parser.add_argument("--n", type=int, default=100_000)
parser.add_argument("--number", type=int, default=100)
parser.add_argument("--repeats", type=int, default=5)
args = parser.parse_args()

SIZE = args.n
LOOKUPS = args.number
REPEATS = args.repeats

values = list(range(SIZE))
values_set = set(values)

# Hit queries are near the end of the list; misses aren't present.
hits = [SIZE - 1] * LOOKUPS
misses = [SIZE + 1] * LOOKUPS


def count_hits(collection, queries):
    return sum(value in collection for value in queries)


for label, queries in [("hits", hits), ("misses", misses)]:
    assert count_hits(values, queries) == count_hits(values_set, queries)

    for collection_name, collection in [
        ("list", values),
        ("set", values_set),
    ]:
        samples = repeat(
            lambda collection=collection, queries=queries: count_hits(collection, queries),
            number=10,
            repeat=REPEATS,
        )
        print(
            f"{label:6} {collection_name:4}: "
            f"{min(samples) / 10:.6f}s per call"
        )
