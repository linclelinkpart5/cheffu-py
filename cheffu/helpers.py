import itertools


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
