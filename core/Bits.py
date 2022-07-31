import typing
from abc import ABC

from core.Data import Data
from core.Wire import Wire
from core.utils import *
from core.operations import PrimOp


class Element(Data, ABC):
    def __init__(self, direction: Direction, width: int):
        self.width = width
        super(Element, self).__init__(direction)

    def collectElms(self) -> None:
        return None

    def getWidth(self) -> int:
        return self.width


class _Bits(Element, ABC):
    def __init__(self, direction: Direction, width: int):
        self.width = width
        self._litValue: int | None = None
        super(_Bits, self).__init__(direction, width)

    def litValue(self) -> int:
        return self._litValue if self._litValue is not None else -1

    def isLitValue(self) -> bool:
        return self._litValue is not None

    def setLitValue(self, x: int) -> None:
        self._litValue = x

    def flatten(self) -> list['Data']:
        return [self]

    def __call__(self, *args):
        from core.Bool import Bool
        from core.UInt import _UInt, UInt
        match args:
            case int(x):
                d = Bool(self.direction)
                if self.isLitValue():
                    d.setLitValue((self.litValue() >> x) & 1)
                pushCommand(DefPrim(d.defined().idx, d.toType(), PrimOp.BitSelectOp, [self.ref], [x]))
                return d
            case _UInt() as x:
                self.__call__(x.litValue())
            case int(x), int(y):
                d = UInt(width=(x - y + 1))
                if self.isLitValue():
                    mask = (1 << d.getWidth()) - 1
                    d.setLitValue((self.litValue() >> y) & mask)
                pushCommand(DefPrim(d.defined().idx, d.toType(), PrimOp.BitsExtractOp, [self.ref], [x, y]))
                return d
            case _UInt(), _UInt() as x, y:
                self.__call__(x.litValue(), y.litValue())
            case _:
                raise ValueError(f'unsupported args for bits: {args}')

    def __ilshift__(self, other: '_Bits'):
        pushCommand(ConnectPad(self.ref, other.ref))

    def fromBits(self, n: '_Bits') -> '_Bits':
        res = Wire(self.cloneType())
        res <<= n
        return res

    def _bitsUnOp(self, op: PrimOp) -> '_Bits':
        d = self.cloneTypeWidth(-1)
        pushCommand(DefPrim(d.defined().idx, d.toType(), op, [self.ref], NoLits))
        return d

    def _bitsBinOp(self, op: PrimOp, other: typing.Union[int, '_Bits']) -> '_Bits':
        d = self.cloneTypeWidth(-1)
        if isinstance(other, int):
            pushCommand(DefPrim(d.defined().idx, d.toType(), op, [self.ref], [other]))
        else:
            pushCommand(DefPrim(d.defined().idx, d.toType(), op, [self.ref, other.ref], NoLits))
        return d

    def _bitsBinOpPad(self, op: PrimOp, other: '_Bits') -> '_Bits':
        d = self.cloneTypeWidth(-1)
        pushCommand(DefPrimPad(d.defined().idx, d.toType(), op, [self.ref, other.ref], NoLits))
        return d

    def _bitsCompareOpPad(self, op: PrimOp, other: '_Bits') -> '_Bool':
        from core.Bool import Bool
        d = Bool(self.direction)
        pushCommand(DefPrimPad(d.defined().idx, d.toType(), op, [self.ref, other.ref], NoLits))
        return d
    
    def _bitsReduceOp(self, op: PrimOp) -> '_Bool':
        from core.Bool import Bool
        d = Bool(self.direction)
        pushCommand(DefPrim(d.defined().idx, d.toType(), op, [self.ref], NoLits))
        return d

    def __neg__(self) -> '_Bits':
        return self._bitsUnOp(PrimOp.NegOp)

    def __add__(self, other: '_Bits') -> '_Bits':
        return self._bitsBinOpPad(PrimOp.AddOp, other)

    def addMod(self, other: '_Bits') -> '_Bits':
        return self._bitsBinOpPad(PrimOp.AddModOp, other)

    def __sub__(self, other: '_Bits') -> '_Bits':
        return self._bitsBinOpPad(PrimOp.SubOp, other)

    def subMod(self, other: '_Bits') -> '_Bits':
        return self._bitsBinOpPad(PrimOp.SubModOp, other)

    def __mul__(self, other: '_Bits') -> '_Bits':
        return self._bitsBinOpPad(PrimOp.TimesOp, other)

    def __truediv__(self, other: '_Bits') -> '_Bits':
        return self._bitsBinOpPad(PrimOp.DivideOp, other)

    def __mod__(self, other: '_Bits') -> '_Bits':
        return self._bitsBinOpPad(PrimOp.ModOp, other)

    def __lshift__(self, other: typing.Union[int, '_Bits']) -> '_Bits':
        if isinstance(other, int):
            return self._bitsBinOp(PrimOp.ShiftLeftOp, other)
        else:
            return self._bitsBinOp(PrimOp.DynamicShiftLeftOp, other)

    def __rshift__(self, other: typing.Union[int, '_Bits']) -> '_Bits':
        if isinstance(other, int):
            return self._bitsBinOp(PrimOp.ShiftRightOp, other)
        else:
            return self._bitsBinOp(PrimOp.DynamicShiftRightOp, other)

    def __invert__(self) -> '_Bits':
        return self._bitsUnOp(PrimOp.BitNotOp)

    def __and__(self, other: '_Bits') -> '_Bits':
        r = self._bitsBinOpPad(PrimOp.BitAndOp, other)
        if self.isLitValue() and other.isLitValue():
            r.setLitValue(self.litValue() & other.litValue())
        return r

    def __or__(self, other: '_Bits') -> '_Bits':
        return self._bitsBinOpPad(PrimOp.BitOrOp, other)

    def __xor__(self, other: '_Bits') -> '_Bits':
        return self._bitsBinOpPad(PrimOp.BitXorOp, other)

    def __lt__(self, other: '_Bits') -> '_Bool':
        return self._bitsCompareOpPad(PrimOp.LessOp, other)

    def __gt__(self, other: '_Bits') -> '_Bool':
        return self._bitsCompareOpPad(PrimOp.GreaterOp, other)

    def __eq__(self, other: '_Bits') -> '_Bool':
        if not isinstance(other, Data):
            raise TypeError('Data can only compare with another Data!')
        r = self._bitsCompareOpPad(PrimOp.EqualOp, other)
        if self.isLitValue() and other.isLitValue():
            r.setLitValue(1 if self.litValue() == other.litValue() else 0)
        return r

    def __ne__(self, other: '_Bits') -> '_Bool':
        return self._bitsCompareOpPad(PrimOp.NotEqualOp, other)
    
    def __le__(self, other: '_Bits') -> '_Bool':
        return self._bitsCompareOpPad(PrimOp.LessEqOp, other)

    def __ge__(self, other: '_Bits') -> '_Bool':
        return self._bitsCompareOpPad(PrimOp.GreaterEqOp, other)
    
    def pad(self, other: int) -> '_Bits':
        return self._bitsBinOp(PrimOp.PadOp, other)
    
    def orR(self) -> '_Bool':
        return self._bitsReduceOp(PrimOp.OrReduceOp)
    
    def andR(self) -> '_Bool':
        return self._bitsReduceOp(PrimOp.AndReduceOp)

    def xorR(self) -> '_Bool':
        return self._bitsReduceOp(PrimOp.XorReduceOp)
    
    def bitSet(self, off: int, data: '_Bits') -> '_Bits':
        from core.UInt import UInt
        bit = UInt(1, 1) << off
        return (self & ~bit) | (data.toSInt() & bit)

    def toBools(self) -> '_Vec':  # TODO
        ...

    @abc.abstractmethod
    def fromInt(self, x: int) -> '_Bits':
        ...

    def toSInt(self) -> '_SInt':
        from core.SInt import SInt
        return chiselCast(self, SInt())

    def toUInt(self) -> '_UInt':
        from core.UInt import UInt
        return chiselCast(self, UInt())

    """
    def cloneType(self) -> 'Data':
        ...

    def cloneTypeWidth(self, width: int) -> 'Data':
        ...

    def toType(self) -> Kind:
        ...
    """


def Bits(*args) -> _Bits:
    from core.UInt import UInt, unitLit
    from Literal import string2Val
    match args:
        case Direction() as d, int(w):
            return UInt(d, w)
        case int(v), int(w):
            return unitLit(v, w)
        case int(v), :
            return Bits(v, -1)
        case str(n), int(w):
            return Bits(string2Val(n[0], n[1:]), w)
        case str(n), :
            return Bits(n, -1)
        case _:
            raise ValueError(f'Unsupported args for instantiate Bits: {args}')


if __name__ == '__main__':
    from core.Module import Module
    pushModule(Module())
    pushCommands()
    bits = Bits(INPUT, 1)
    print(bits)
    s = bits.toSInt()
    print(s)
