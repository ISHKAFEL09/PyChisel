from core.Bits import _Bits, Bits
from core.Bool import _Bool
from core.Literal import *
from core.utils import *
from core.Data import Data


class _MInt(Data):
    def __init__(self, value: str, width: int):
        super(_MInt, self).__init__(NO_DIR)
        self._value = value
        self._width = width
        self._bits, self._mask, self._sWidth = parseLit(value)

    def direction(self) -> Direction:
        return NO_DIR

    def setDirection(self, direction: Direction) -> None:
        ...

    def toType(self) -> UIntType:
        return UIntType(UnknownWidth, self.isFlip)

    def cloneType(self) -> '_MInt':
        return _MInt(self._value, self._width)

    def cloneTypeWidth(self, width: int) -> '_MInt':
        return self.cloneType()

    def getWidth(self) -> int:
        return self._width

    def flatten(self) -> list[_Bits]:
        return [Bits(0)]

    def collectElms(self) -> None:
        ...

    def zEquals(self, other: _Bits) -> _Bool:
        return (Bits(toLitVal(self._mask, 2)) & other) == Bits(toLitVal(self._bits, 2))

    def __eq__(self, other: _Bits) -> _Bool:
        return self.zEquals(other)

    def __ne__(self, other: _Bits) -> _Bool:
        return ~self.zEquals(other)


def MInt(*args) -> _MInt:
    ...


def fromInt(x: int) -> '_MInt':
    return MInt(bin(x)[1:], -1)


if __name__ == '__main__':
    from core.Data import _FakeData
    fake_data = _FakeData()
    mint = _MInt('1010_0101_??11', 1)
    # print(mint.flatten())
    print(mint._bits, mint._mask, mint._sWidth)
    print(toLitVal(mint._bits, 2))
