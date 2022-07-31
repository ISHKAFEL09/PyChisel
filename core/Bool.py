from abc import ABC

from .Bits import _Bits


class _Bool(_Bits, ABC):
    ...


def Bool(*args) -> _Bool:
    ...
