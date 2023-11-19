import itertools
from typing import Any, Iterable, List


def pairwise(iterable: List[Any]) -> Iterable[Any]:
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
