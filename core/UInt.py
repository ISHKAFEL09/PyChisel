from abc import ABC

from core.utils import *
from core.Bits import _Bits


class _UInt(_Bits):
    def __init__(self, direction: Direction, value: int):
        super(_UInt, self).__init__(direction)
        self._value = value

    def fromInt(self, x: int) -> '_Bits':
        ...

    def toType(self) -> Kind:
        pass

    def cloneType(self) -> 'Data':
        pass

    def cloneTypeWidth(self, width: int) -> 'Data':
        pass


def unitLit(value: int, width: int) -> _UInt:
    w = max(value.bit_length(), 1) if width == -1 else width
    b = _UInt(NO_DIR, value)


def UInt(*args, **kwargs) -> _UInt:
    return _UInt(INPUT, 1)
