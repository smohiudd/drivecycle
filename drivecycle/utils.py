import itertools
from typing import List, Iterable, Any


def pairwise(iterable: List[Any]) -> Iterable[Any]:
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)
