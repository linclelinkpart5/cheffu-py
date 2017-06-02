import itertools
import contextlib
import math
import typing as typ


def partition(pred, iterable):
    """From Python itertools recipes. Uses a predicate to partition entries into false entries and true entries."""
    # partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9
    t1, t2 = itertools.tee(iterable, 2)
    return itertools.filterfalse(pred, t1), filter(pred, t2)


def pairwise(iterable):
    """From Python itertools recipes. Iterates over consecutive pairs in an iterable."""
    a, b = itertools.tee(iterable, 2)
    next(b, None)
    return zip(a, b)


@contextlib.contextmanager
def empty_context():
    """A context manager that does nothing, mainly useful for (unit) testing.
    """
    yield


def yield_sum_splits(n: int) -> typ.Iterable[typ.Tuple[int, int]]:
    """Given an integer, returns all possible sum splits.

    For example, 5 -> (0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0).
    """
    sign = int(math.copysign(1, n))
    an = abs(n)
    for i in range(an + 1):
        yield (sign * i, sign * (an - i))
