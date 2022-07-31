from abc import ABC

from core.utils import *
from core.Bits import _Bits


class _SInt(_Bits, ABC):
    def fromInt(self, x: int) -> '_Bits':
        ...


def unitLit(value: int, width: int) -> _SInt:
    w = max(value.bit_length(), 1) if width == -1 else width
    b = _SInt()


def SInt(*args, **kwargs) -> _SInt:
    return _SInt(INPUT, 1)
